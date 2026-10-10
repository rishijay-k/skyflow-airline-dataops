#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
umask 077
terraform fmt -check
terraform validate
set +e
terraform plan -input=false -detailed-exitcode -no-color -out=verified.tfplan > verified-plan.log 2>&1
result=$?
set -e
cat verified-plan.log
if [ "$result" -ne 0 ]; then
  echo "STOP: plan failed or proposed changes; do not apply."
  exit 1
fi
terraform show -json verified.tfplan > verified-plan.json
python3 check-plan.py verified-plan.json
