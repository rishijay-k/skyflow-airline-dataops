"""Verify exact published events end to end, not unrelated row-count growth."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import time
from datetime import datetime, timezone

from google.cloud import bigquery, pubsub_v1

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src" / "streaming"))
from publish_live_events import create_event

PROJECT = "skyflow-511113"
REGION = "asia-south1"
TABLE = f"{PROJECT}.skyflow_raw.flight_events_streaming"


def inspect_rows(expected, rows):
    """Return acceptance counts; every event must have its actual publish ID."""
    seen = {}
    wrong_message_ids = 0
    for row in rows:
        event_id = row["event_id"]
        if event_id not in expected:
            continue
        seen[event_id] = seen.get(event_id, 0) + 1
        wrong_message_ids += row["pubsub_message_id"] != expected[event_id]
    missing = len(set(expected) - set(seen))
    duplicates = sum(count - 1 for count in seen.values())
    return dict(expected_events=len(expected), matched_events=len(seen),
                missing_events=missing, duplicate_rows=duplicates,
                wrong_message_ids=wrong_message_ids,
                passed=bool(expected) and not (missing or duplicates or wrong_message_ids))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="logs/streaming-verification.json")
    args = parser.parse_args()
    output = ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    log_path = ROOT / "logs/streaming_verification_consumer.log"
    log_path.parent.mkdir(exist_ok=True)
    bq = bigquery.Client(project=PROJECT, location=REGION)
    publisher = pubsub_v1.PublisherClient()
    subscriber = pubsub_v1.SubscriberClient()
    consumer = None
    report = {"project": PROJECT, "region": REGION,
              "started_at": datetime.now(timezone.utc).isoformat(), "passed": False}
    try:
        topic = publisher.topic_path(PROJECT, "skyflow-flight-events")
        subscription = subscriber.subscription_path(PROJECT, "skyflow-flight-events-sub")
        publisher.get_topic(request={"topic": topic}, timeout=30)
        subscriber.get_subscription(request={"subscription": subscription}, timeout=30)
        bq.get_table(TABLE, timeout=30)
        print("PASS: existing topic, subscription and table found", flush=True)
        with log_path.open("w") as log:
            consumer = subprocess.Popen(
                [sys.executable, "-u", "src/streaming/stream_to_bigquery.py"],
                cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
            expected = {}
            for _ in range(20):
                event = create_event()
                message_id = publisher.publish(topic, json.dumps(event).encode(),
                                               event_type=event["event_type"]).result(timeout=30)
                expected[event["event_id"]] = message_id
            print("Published 20 uniquely identified synthetic events", flush=True)
            code = consumer.wait(timeout=190)
            if code:
                raise RuntimeError("Consumer did not complete; inspect its local log")
            config = bigquery.QueryJobConfig(
                maximum_bytes_billed=100 * 1024 * 1024,
                query_parameters=[bigquery.ArrayQueryParameter("ids", "STRING", list(expected))])
            deadline = time.monotonic() + 60
            while True:
                rows = bq.query(
                    f"SELECT event_id, pubsub_message_id FROM `{TABLE}` "
                    "WHERE event_id IN UNNEST(@ids)", job_config=config,
                    location=REGION, timeout=30).result(timeout=30)
                counts = inspect_rows(expected, rows)
                if counts["passed"] or time.monotonic() >= deadline:
                    break
                time.sleep(2)
            report.update(counts)
            report["event_message_ids"] = expected
            if not counts["passed"]:
                raise RuntimeError("Exact-event verification failed")
            print("PASS: all 20 exact event IDs and Pub/Sub message IDs verified; no duplicates")
    except Exception as error:
        report["passed"] = False
        report["error_type"] = type(error).__name__
        print(f"FAIL: {type(error).__name__}; inspect {log_path}", file=sys.stderr)
    finally:
        if consumer is not None and consumer.poll() is None:
            consumer.terminate()
            try:
                consumer.wait(timeout=10)
            except subprocess.TimeoutExpired:
                consumer.kill()
                consumer.wait()
        publisher.stop()
        subscriber.close()
        bq.close()
        report["finished_at"] = datetime.now(timezone.utc).isoformat()
        output.write_text(json.dumps(report, indent=2) + "\n")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
