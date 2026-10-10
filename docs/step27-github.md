# Step 27 — GitHub preparation

The local repository contains the pipeline source, SQL, Terraform configuration, tests and a project README. Generated data, logs, virtual environments, credentials, private Terraform inputs, state and plans are excluded.

## Review on your Mac

```bash
cd ~/Projects/skyflow
source .venv/bin/activate
python -m pytest -q
git status --short
```

Expected: 26 tests pass. Before the first commit, files appear as untracked (`??`).

Inspect the exact file list eligible for addition:

```bash
git ls-files --others --exclude-standard
```

Check the key exclusions:

```bash
git check-ignore .venv/ infra/terraform/terraform.tfstate infra/terraform/terraform.tfvars infra/terraform/verified.tfplan
```

The source/configuration and `.terraform.lock.hcl` should be committed. Never force-add ignored state, credentials or generated outputs.

## Publishing is a separate step

Published publicly at https://github.com/rishijay-k/skyflow-airline-dataops. The repository name and visibility were approved before publishing.

The README describes the implemented scope. Continuous integration is implemented in Step 28; automated deployment and AI diagnostics remain planned.
