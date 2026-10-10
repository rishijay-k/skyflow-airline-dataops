# Step 26 — offline automated tests

Run from Mac Terminal:

```bash
cd ~/Projects/skyflow
source .venv/bin/activate
python -m pytest -q
```

Pytest is already in requirements.txt and installed in the project environment.

The 26 test cases cover generated event routes, IDs, timestamps and delays; writing 1,000 JSON lines into a temporary directory; healthy and failed quality gates; streaming ACK after a successful write, NACK on missing fields, malformed JSON, rejected rows or write exceptions; batch success and failure observability records and failed process exit status.

Cloud clients and the batch subprocess are mocked before use. No credentials or live GCP calls are needed. These tests do not replace Step 24 streaming integration verification or exercise the actual BigQuery SQL transformations.

Known limits discovered during inspection:

- The batch generator picks flight_status independently from event_type. CLEAN SQL normalizes status; raw events are not guaranteed status-consistent.
- The streaming callback checks missing keys, but does not validate every field value locally. Invalid values may be rejected by BigQuery.
- Streaming timeout exit behavior is now covered by six regression cases: success returns 0, incomplete/timeout returns 1, and interruption returns 130. Subscriber cleanup is verified.
- Observability records the total RAW row count, not a independently measured count of records processed by a run.

These are existing behaviors, not fixed or hidden by this test suite. Production hardening should address them separately.
