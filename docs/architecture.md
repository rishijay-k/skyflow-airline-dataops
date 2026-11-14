# Architecture and design decisions

## Data paths

Batch: Python generator → JSONL → BigQuery RAW → SQL CLEAN → CURATED airport/route metrics → quality gate. CLEAN preserves the raw status and derives a normalized status from event type.

Streaming: Python publisher → Pub/Sub topic/subscription → Python consumer → a separate BigQuery streaming RAW table → OPS streaming health and airport views. The consumer acknowledges after an accepted write. Insert IDs reduce some duplicate risk but are not an exactly-once guarantee.

Observability: the observed batch wrapper runs the batch script and writes an outcome to pipeline_runs. Its records_processed field currently reflects the final RAW row count. The diagnostic collector uses fixed SELECT queries over streaming_health and latest pipeline_runs records, with query limits and timeouts.

AI: deterministic findings → bounded prompt → Abacus RouteLLM → schema-validated explanation → human review. The model receives findings, not unrestricted warehouse access. It cannot call tools or execute repairs through this program. OpenAI is an optional adapter whose live verification remains incomplete.

## Infrastructure and delivery

Project: skyflow-511113. BigQuery location: asia-south1. Pub/Sub resource names are global. Terraform adopts four datasets plus the topic/subscription, retaining existing settings. Lifecycle guards and non-destructive plan checks help prevent accidental replacement; they are not cloud-side deletion locks. State and private variables remain local and excluded from Git.

GitHub Actions runs Python tests, dependency checks, shell syntax checks and Terraform formatting/validation. It has no GCP credentials and does not deploy, apply Terraform or execute live pipeline jobs. The repository is currently tied to the existing project; a clean clone is not a one-command full deployment.

## Verification record

- October 10, 2026: batch/streaming verification and Terraform zero-change adoption were established during project development.
- November 15, 2026: Abacus demo and live-monitoring explanation outputs were confirmed from user screenshots.
- The latest CI run provides commit-specific offline validation. See the repository Actions page.

These are point-in-time results, not a claim of continuous production uptime. Screenshot-based AI acceptance does not imply that new flight events were generated that day.
