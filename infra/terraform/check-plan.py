import json
import sys
expected = {
    "google_bigquery_dataset.skyflow_raw",
    "google_bigquery_dataset.skyflow_clean",
    "google_bigquery_dataset.skyflow_curated",
    "google_bigquery_dataset.skyflow_ops",
    "google_pubsub_topic.flight_events",
    "google_pubsub_subscription.flight_events",
}
with open(sys.argv[1]) as stream:
    plan = json.load(stream)
resources = plan.get("resource_changes", [])
if {r["address"] for r in resources} != expected:
    sys.exit("STOP: expected exactly six managed resources")
for resource in resources:
    change = resource["change"]
    if change["actions"] != ["no-op"] or change.get("importing"):
        sys.exit("STOP: unexpected changes to " + resource["address"])
print("PASS: all six resources are imported; 0 add, 0 change, 0 destroy.")
