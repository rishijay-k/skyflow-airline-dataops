# SkyFlow portfolio acceptance

Scope: the original **on-demand portfolio project**, as confirmed by the owner. Continuous production deployment is outside this acceptance scope. This is not a claim that a software system is permanently error-free.

## Final acceptance — November 15, 2026 (Asia/Kolkata)

| Deliverable | Evidence | Result |
|---|---|---|
| Batch pipeline and SQL models | [Batch run output](evidence/batch.txt): 1,000 RAW/CLEAN rows, 90 routes | Passed |
| Quality gates | 10/10 checks in the fresh batch run | Passed |
| Streaming path | [Exact-event verification](evidence/acceptance.json): 20/20 events and matching Pub/Sub IDs | Passed |
| Operational monitoring | [Fresh snapshot](evidence/diagnostics.json): latest batch SUCCESS; 20 recent events | Passed |
| Terraform adoption and preservation | Six managed resources; final plan 0 add / 0 change / 0 destroy | Passed |
| Offline tests | 58 tests, including missing, duplicate and mismatched streaming evidence | Passed |
| Repository and CI | [GitHub Actions](https://github.com/rishijay-k/skyflow-airline-dataops/actions/workflows/ci.yml) tests and validates each commit | See release commit's run |
| AI diagnostics | Live Abacus `route-llm` call returned a validated explanation | Passed |
| Documentation and demo | Architecture, recovery runbook, narrated MP4, chapter index and transcript | Included in v1.0.0 release |

Machine-readable evidence: [acceptance.json](evidence/acceptance.json). The captured run timestamps use UTC; November 14 at 21:41 UTC is November 15 at 03:11 in India.

## Failure found and repaired

The final audit found `skyflow-flight-events-sub` missing. Terraform proposed creating only that subscription, and the Google Cloud CLI independently returned NOT_FOUND. The previous configuration used a 31-day inactivity expiry; this is consistent with the gap since October 10, but the exact deletion cause was not established from audit logs.

A reviewed saved Terraform plan restored only the missing subscription and disabled idle expiration. The four existing BigQuery datasets and Pub/Sub topic were unchanged. A second plan then returned zero changes. The original six-resource import is historical; this later recovery is a separate, explicitly documented operation.

The streaming acceptance test was also strengthened. It now verifies the exact 20 published event IDs and their actual Pub/Sub message IDs rather than relying on total table growth. It fails on missing events, duplicate rows or mismatched message IDs, and cleans up its consumer process on failure.

## Honest boundaries

- This is synthetic airline data, with no airline affiliation or production traffic.
- Evidence proves the recorded executions; it is not continuous uptime monitoring.
- AI explains fixed diagnostic findings. It does not choose tools or repair infrastructure.
- The accepted provider is Abacus. Optional OpenAI live acceptance is not required and remains unverified.
- CI is implemented; continuous deployment is outside the confirmed scope.
- Duplicate delivery and incomplete input validation remain documented engineering limitations, not hidden production guarantees.
- The MP4 is an evidence-based narrated walkthrough with computer-generated speech, not footage of a live terminal session.

## Reproduce

Follow [the runbook](runbook.md) for commands and expected outcomes. Follow [the demo guide](demo.md) to view or regenerate the finished media. A later run may legitimately differ; never overwrite a failure with a completion claim.
