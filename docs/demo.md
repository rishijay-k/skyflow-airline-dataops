# SkyFlow finished demo

The finished **3-minute-47-second MP4** is attached to the [v1.0.0 release](https://github.com/rishijay-k/skyflow-airline-dataops/releases/tag/v1.0.0). It uses captured live acceptance results and macOS computer-generated narration. It is not a recording of a live terminal session.

- [Download video](https://github.com/rishijay-k/skyflow-airline-dataops/releases/download/v1.0.0/SkyFlow-demo.mp4)
- [Read transcript](demo/transcript.md)
- [Chapter index](demo/chapters.vtt)
- [Acceptance evidence](completion.md)

## Regenerate the narrated video on macOS

This uses a separate media environment and makes no cloud calls.

```bash
cd ~/Projects/skyflow
python3 -m venv /tmp/skyflow-demo-venv
/tmp/skyflow-demo-venv/bin/python -m pip install -r requirements-demo.txt
/tmp/skyflow-demo-venv/bin/python scripts/build_demo.py --output /tmp/skyflow-demo
open /tmp/skyflow-demo/SkyFlow-demo.mp4
```

The storyboard is tied to the recorded November 15 acceptance evidence. Update it with newly verified results before making claims about a later run.

## Optional live presentation

The following walkthrough is for presenting the project interactively; the finished media does not require you to record it again.

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

Expected: 58 tests pass. Then open the latest successful run under GitHub Actions. Explain that these are offline tests with mocked cloud/model calls plus Terraform validation, not a full live integration test.

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

## Optional screen recording

Record a selected screen area with macOS screen recording (Shift-Command-5). Keep API-key pages, `.env`, Terraform state, personal tabs and notifications out of frame. Start with the README, show the commands above, and finish on the CI result. Save a 3–5 minute video and add its link to the README once uploaded. The release already includes the narrated evidence video; this is an optional separate screen recording.
