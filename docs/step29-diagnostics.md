# Step 29 — read-only diagnostics with OpenAI explanations

Implemented locally: evidence collection, deterministic checks, optional OpenAI Responses API explanations, demo mode and offline tests. Live BigQuery collection has been verified. Live OpenAI verification is pending an API key and an account with model access/billing.

This is an AI-assisted diagnostic workflow. It uses fixed read-only queries and one model call; it is not an autonomous remediation agent or a model-driven tool-selection loop.

## Run without an API key

```bash
cd ~/Projects/skyflow
source .venv/bin/activate
python src/agent/diagnose.py --demo
python src/agent/diagnose.py
```

The first command uses synthetic evidence; the second reads existing BigQuery monitoring data. No AI request is made unless `--ai` is specified. Add `--expect-streaming` when a producer/consumer run is expected now. Inactivity otherwise stays informational for this on-demand demo.

## Configure OpenAI privately

Create a key in your OpenAI API project: https://platform.openai.com/api-keys

Then in Mac Terminal:

```bash
cd ~/Projects/skyflow
source .venv/bin/activate
python scripts/configure_openai.py
```

Paste the key at the hidden prompt and press Enter. Characters will not appear while pasting. The helper writes only the OPENAI_API_KEY setting to your local `.env`, preserves other settings, and restricts file permissions. Do not paste the key into chat or commit `.env`.

```bash
python src/agent/diagnose.py --demo --ai
python src/agent/diagnose.py --ai
```

Both `--ai` commands send findings to OpenAI and use API billing. The default model is `gpt-4.1-mini`; override with `--model` only for a Responses/Structured Outputs compatible model your account can access. API model access and billing must be configured separately from this repository.

## Evidence and boundaries

Two fixed SELECT queries read `skyflow_ops.streaming_health` and the latest observed run per pipeline from `skyflow_ops.pipeline_runs`. Each query has a 100 MiB maximum bytes billed setting and bounded waits. Raw pipeline error strings are omitted. This prevents logs or credentials in error text from being forwarded to the model.

Rules flag duplicate/null IDs, failed batch runs, unavailable evidence, and inactivity. Available metrics that trigger no flags do not prove end-to-end health. The current rules do not assess every metric or enforce a batch freshness SLA.

OpenAI receives the collection time, demo/live flag and rule findings (including pipeline names and start times for flagged runs). It does not receive raw flight rows, credentials or Terraform state. Its response separates summary, hypotheses, suggested checks and limitations. Inputs are treated as untrusted data. The model is not given tools, shell access or write operations. Advice may still be wrong and must be reviewed.

Requests use `store: false`, a 1,000-token output cap, a bounded input, and timeouts. Refusals, incomplete responses, invalid structures and API errors are treated as failures; deterministic evidence is retained. This is not a zero-data-retention guarantee.

Exit code 0 means a report was produced; the report can still contain ERROR findings. Exit code 2 means evidence collection or a requested AI explanation failed. Missing credentials fail before cloud queries.

## Validation

```bash
python -m pytest -q
```

Current suite: 41 offline cases. CI requires no OpenAI key; API success/error responses are mocked. A real successful `--ai` run is still required to complete Step 29 acceptance.

Sources:
- https://developers.openai.com/api/docs/guides/structured-outputs?api-mode=responses
- https://developers.openai.com/api/docs/models/gpt-4.1-mini
