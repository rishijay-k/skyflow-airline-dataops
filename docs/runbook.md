# SkyFlow runbook

## Start

```bash
cd ~/Projects/skyflow
source .venv/bin/activate
python -m pytest -q
```

Expected for release v1.0.0: 58 passed. This uses no cloud credentials or model calls.

## Inspect infrastructure

```bash
bash infra/terraform/verify-plan.sh
```

Expected: six managed resources and zero additions, changes or deletions. A plan that proposes changes is a failure of this acceptance gate. Do not apply it blindly. Local state and `terraform.tfvars` are private and must remain outside Git. Back up local state securely before migration; do not import the same resources into a second active state.

If a resource is missing, confirm that with the relevant Google Cloud describe command, inspect the exact Terraform changes, and preserve all existing resources. The November 15 repair restored a missing subscription; the committed configuration now disables its idle expiry. The saved repair plan is local evidence, not a reusable deployment artifact.

## Run the batch demo

```bash
python src/monitoring/run_observed_batch.py
```

This deliberately replaces synthetic RAW batch data, rebuilds CLEAN/CURATED models and appends an operational run record. Expect `Run status: SUCCESS`, 1,000 records and 10/10 quality checks. It uses billable cloud resources. If it fails, inspect the failing stage before rerunning; a successful historical run does not override a current failure.

## Verify streaming

```bash
bash scripts/verify_streaming_pipeline.sh
```

This starts a bounded consumer, publishes 20 synthetic events, waits for accepted writes and queries their exact IDs. Expect 20 matched events, zero missing events, zero duplicate rows and zero wrong message IDs. Detailed output is in ignored `logs/streaming-verification.json` and the consumer log. Existing queued messages or concurrent consumers can cause a real test failure; do not purge the subscription or delete existing data to conceal it.

## Run diagnostics

```bash
python src/agent/diagnose.py --demo
python src/agent/diagnose.py
python src/agent/diagnose.py --ai --provider abacus
```

The first command is synthetic and offline. The second queries monitoring. The third also uses Abacus credits and requires the private key configured with `python scripts/configure_abacus.py`. Never put the key in source, screenshots or a command argument. A stale exported `ABACUS_API_KEY` can override the local `.env` setting; use `unset ABACUS_API_KEY` if that is the problem.

An idle stream is normal when the on-demand producer is stopped. Use `--expect-streaming` only when activity is actually expected. A no-flags report is limited to the available rules and evidence. API failures preserve deterministic findings and return a failing exit status for the requested explanation.

## Common failures

| Symptom | Next action |
|---|---|
| Missing subscription | Confirm `gcloud pubsub subscriptions describe skyflow-flight-events-sub --project=skyflow-511113`; inspect the Terraform plan before recovery |
| Google authentication expired | Run `gcloud auth application-default login`; then `gcloud auth application-default set-quota-project skyflow-511113` |
| Missing or duplicated verification events | Inspect the consumer log, backlog and competing consumers; retain the failing evidence |
| Abacus 401 | Configure the actual RouteLLM API key, not an OpenAI key |
| Abacus 429 | Check that account's credits and request limits; repeated retries do not fix missing credits |
| Terraform changes proposed | Review drift; never use `destroy` or `apply` merely to obtain a green demo |

## Release and media

The repository contains source and timestamped evidence. Large MP4 media is attached to the v1.0.0 GitHub release. The video is reproducible on macOS using `scripts/build_demo.py`, `requirements-demo.txt`, and `docs/demo/storyboard.json`; see the demo guide. The generator makes no cloud calls and reads no private configuration.
