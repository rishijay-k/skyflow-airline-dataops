# SkyFlow demo — 3 to 5 minutes

## 1. Explain the problem (30 seconds)

“SkyFlow is a portfolio platform for synthetic airline events. It combines batch modelling and event streaming with quality checks, operational monitoring and AI-assisted diagnostics.”

Show the README architecture. Explain that batch and streaming have separate RAW tables; streaming has operational views but is not merged into the batch CLEAN/CURATED tables.

## 2. Show tests and CI (45 seconds)

In Mac Terminal:

```bash
cd ~/Projects/skyflow
source .venv/bin/activate
python -m pytest -q
```

Expected: 51 tests pass. Then open the latest successful run under GitHub Actions. Explain that these are offline tests with mocked cloud/model calls plus Terraform validation, not a full live integration test.

## 3. Show Terraform adoption (45 seconds)

```bash
cd ~/Projects/skyflow/infra/terraform
terraform state list
bash verify-plan.sh
cd ~/Projects/skyflow
```

Expected: six imported resources and zero changes. If the plan fails or proposes changes, stop and inspect it. Do not apply just to make the demo green. Explain that existing resources were imported rather than recreated.

## 4. Show diagnostics (60 seconds)

No-API option:

```bash
python src/agent/diagnose.py --demo
```

Abacus synthetic demo (uses API credits):

```bash
python src/agent/diagnose.py --demo --ai --provider abacus
```

Live monitoring plus Abacus (BigQuery queries and API usage):

```bash
python src/agent/diagnose.py --ai --provider abacus
```

Show the mode, evidence, explanation and limitations. Synthetic failures are deliberately injected examples, not real outages. Zero events in five minutes can be normal when the on-demand producer is idle. A historical successful batch does not prove current health. The model suggests checks; it does not execute repairs.

## 5. Close with scope (30 seconds)

“Terraform manages the existing datasets and Pub/Sub resources. CI tests changes. AI explains bounded diagnostic findings for human review. Next improvements would be stronger event validation, deduplication and fully reproducible provisioning.”

## Optional fresh pipeline evidence

Only run these when you intentionally want to regenerate demo data. The observed batch replaces RAW batch data and rebuilds downstream batch tables. Streaming verification publishes more events and may consume existing queued messages. Both use cloud resources.

```bash
cd ~/Projects/skyflow
source .venv/bin/activate
python src/monitoring/run_observed_batch.py
bash scripts/verify_streaming_pipeline.sh
```

Do not claim fresh end-to-end success unless these actually pass. The diagnostics screenshots alone do not establish that.

## Recording

Record a selected screen area with macOS screen recording (Shift-Command-5). Keep API-key pages, `.env`, Terraform state, personal tabs and notifications out of frame. Start with the README, show the commands above, and finish on the CI result. Save a 3–5 minute video and add its link to the README once uploaded. A recording has not been created by this guide.
