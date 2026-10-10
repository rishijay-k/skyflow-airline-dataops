# SkyFlow Step 25 — adopt existing infrastructure

Project: `skyflow-511113`. BigQuery location and provider region: `asia-south1`.
Pub/Sub topics and subscriptions have global resource names; the provider region does not relocate them.

## What was built

- `versions.tf`: Terraform >=1.5, Google provider ~>7.0. Commit `.terraform.lock.hcl` to preserve the tested provider version.
- `main.tf`: four existing BigQuery datasets, one Pub/Sub topic, one subscription, generated from live settings. Existing descriptions, access entries, retention, expiration and the 30-second ack deadline are retained.
- `imports.tf`: exact existing resource IDs.
- `import-existing.sh`: CLI imports only; skips addresses already in local state.
- `verify-plan.sh` and `check-plan.py`: require a successful zero-change plan and exactly six resources in state.
- `.gitignore`: keeps local state, plans, logs and backups out of Git.

Dataset tables and views remain in place but are not individually managed by this configuration. APIs, IAM bindings and other project resources are outside this step.

## Beginner-friendly Mac Terminal commands

The files and imports have already been created on this Mac. To verify them, paste:

```bash
cd ~/Projects/skyflow/infra/terraform
pwd
terraform version
terraform init -input=false
terraform state list
bash verify-plan.sh
```

Expected: six addresses and `PASS: all six resources are imported; 0 add, 0 change, 0 destroy.`

`terraform plan` reads live infrastructure and compares it to your configuration. It does not apply changes. No `terraform apply` is necessary for this completed adoption.

## Exact imports used (reference; do not repeat completed imports)

```bash
cd ~/Projects/skyflow/infra/terraform
terraform import google_bigquery_dataset.skyflow_raw projects/skyflow-511113/datasets/skyflow_raw
terraform import google_bigquery_dataset.skyflow_clean projects/skyflow-511113/datasets/skyflow_clean
terraform import google_bigquery_dataset.skyflow_curated projects/skyflow-511113/datasets/skyflow_curated
terraform import google_bigquery_dataset.skyflow_ops projects/skyflow-511113/datasets/skyflow_ops
terraform import google_pubsub_topic.flight_events projects/skyflow-511113/topics/skyflow-flight-events
terraform import google_pubsub_subscription.flight_events projects/skyflow-511113/subscriptions/skyflow-flight-events-sub
```

For a deliberate recovery into an empty local state, `bash import-existing.sh` runs these commands and stops on errors. Never manage the same cloud resource from multiple active states.

## Authentication if a later command reports expired credentials

```bash
gcloud auth application-default login
gcloud auth application-default set-quota-project skyflow-511113
```

Use your existing authorized Google account. Provider project is explicitly fixed in configuration.

## State and deletion protection

State is local at `terraform.tfstate`. Keep it and its backups private and securely backed up. Do not delete state to fix a plan. Commit configuration and the lock file, not state or plan artifacts. A shared remote backend can be added separately when collaboration requires it.

All six resources have `prevent_destroy = true`; datasets also have `delete_contents_on_destroy = false`. These are Terraform guards, not GCP deletion locks. Removing configuration or deleting resources outside Terraform bypasses lifecycle protection. Provider deletion_policy retains its imported value; no policy change was applied during adoption.

The config preserves the existing subscription expiration policy (31 idle days). This is not a guarantee of indefinite GCP retention.

If verification reports changes, stop and inspect `verified-plan.log`. Do not apply or destroy. Match the configuration to the intended live settings before proceeding. Zero changes is the acceptance criterion for Step 25.

## Sources

- https://developer.hashicorp.com/terraform/language/import/generating-configuration
- https://developer.hashicorp.com/terraform/cli/commands/import
- https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/bigquery_dataset

## Private owner configuration

The existing owner email now comes from `var.dataset_owner_email`. This Mac has the correct value in the Git-ignored `terraform.tfvars`. For a deliberate fresh setup, copy `terraform.tfvars.example` to `terraform.tfvars` and supply the actual existing owner before import or plan. Do not commit the private file. This refactor preserves the existing access entries.
