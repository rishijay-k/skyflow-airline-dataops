# Step 28 — GitHub Actions continuous integration

[Open SkyFlow CI](https://github.com/rishijay-k/skyflow-airline-dataops/actions/workflows/ci.yml).

Every push and pull request runs two jobs. You can also choose **Run workflow** on the Actions page.

- **Python tests:** install the pinned requirements on Python 3.12, run `pip check`, execute the offline tests and check shell script syntax.
- **Terraform validation:** use Terraform 1.16.4, check formatting, install the locked provider without a backend, and validate the configuration.

The jobs use read-only repository permissions and actions pinned to commit IDs. They do not need GCP credentials, private variable files or Terraform state. They do not run live pipelines, `terraform plan`, or `terraform apply`.

This implements continuous integration (CI). Automated deployment (CD) remains outside this step. The live zero-change plan remains a separate local check in `infra/terraform/verify-plan.sh`.

## Check locally

From Mac Terminal:

```bash
cd ~/Projects/skyflow
source .venv/bin/activate
python -m pip check
python -m pytest -q
terraform -chdir=infra/terraform fmt -check -recursive
terraform -chdir=infra/terraform validate
```

On GitHub, open **Actions → SkyFlow CI → latest run**. Both jobs must be green for that commit. If a job fails, open the failed step's logs before making changes. A green run validates the tested code/configuration, not live cloud availability.

Required checks/branch protection are not configured by this workflow. A failed run is visible but does not itself block a direct push to main.
