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

No GitHub repository has been created or pushed by this preparation step. Choose the repository name and public/private visibility before publishing. A suitable name is `skyflow-airline-dataops`.

The README describes the implemented scope. CI/CD and AI diagnostics are explicitly marked as planned. Do not describe them as completed features yet.
