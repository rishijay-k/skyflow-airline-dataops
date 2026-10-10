import json
import sys
import threading
from datetime import datetime, timezone

from google.api_core.exceptions import NotFound
from google.cloud import bigquery
from google.cloud import pubsub_v1


# ---------------------------------------------------------
# SKYFLOW CONFIGURATION
# ---------------------------------------------------------

PROJECT_ID = "skyflow-511113"
LOCATION = "asia-south1"

SUBSCRIPTION_ID = "skyflow-flight-events-sub"

DATASET_ID = "skyflow_raw"
TABLE_ID = "flight_events_streaming"

FULL_TABLE_ID = (
    f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"
)

MAX_MESSAGES = 20
WAIT_TIMEOUT_SECONDS = 180


# ---------------------------------------------------------
# EVENT CONTRACT
# ---------------------------------------------------------

REQUIRED_FIELDS = {
    "event_id",
    "flight_id",
    "origin_airport",
    "destination_airport",
    "event_type",
    "event_timestamp",
    "delay_minutes",
    "aircraft_type",
    "flight_status",
}


# ---------------------------------------------------------
# BIGQUERY SCHEMA
# ---------------------------------------------------------

SCHEMA = [
    bigquery.SchemaField(
        "event_id",
        "STRING",
        mode="REQUIRED"
    ),
    bigquery.SchemaField(
        "flight_id",
        "STRING",
        mode="REQUIRED"
    ),
    bigquery.SchemaField(
        "origin_airport",
        "STRING",
        mode="REQUIRED"
    ),
    bigquery.SchemaField(
        "destination_airport",
        "STRING",
        mode="REQUIRED"
    ),
    bigquery.SchemaField(
        "event_type",
        "STRING",
        mode="REQUIRED"
    ),
    bigquery.SchemaField(
        "event_timestamp",
        "TIMESTAMP",
        mode="REQUIRED"
    ),
    bigquery.SchemaField(
        "delay_minutes",
        "INTEGER",
        mode="REQUIRED"
    ),
    bigquery.SchemaField(
        "aircraft_type",
        "STRING",
        mode="REQUIRED"
    ),
    bigquery.SchemaField(
        "flight_status",
        "STRING",
        mode="REQUIRED"
    ),
    bigquery.SchemaField(
        "pubsub_message_id",
        "STRING",
        mode="REQUIRED"
    ),
    bigquery.SchemaField(
        "ingested_at",
        "TIMESTAMP",
        mode="REQUIRED"
    ),
]


# ---------------------------------------------------------
# CLIENTS
# ---------------------------------------------------------

bigquery_client = bigquery.Client(
    project=PROJECT_ID,
    location=LOCATION,
)

subscriber = pubsub_v1.SubscriberClient()

subscription_path = subscriber.subscription_path(
    PROJECT_ID,
    SUBSCRIPTION_ID,
)


# ---------------------------------------------------------
# PROCESS STATE
# ---------------------------------------------------------

received_count = 0

done = threading.Event()

lock = threading.Lock()


# ---------------------------------------------------------
# CREATE TABLE IF NEEDED
# ---------------------------------------------------------

def ensure_streaming_table():

    try:

        bigquery_client.get_table(
            FULL_TABLE_ID
        )

        print(
            f"BigQuery table found: "
            f"{FULL_TABLE_ID}"
        )

    except NotFound:

        table = bigquery.Table(
            FULL_TABLE_ID,
            schema=SCHEMA,
        )

        table.time_partitioning = (
            bigquery.TimePartitioning(
                field="event_timestamp"
            )
        )

        table.clustering_fields = [
            "origin_airport",
            "destination_airport",
            "event_type",
        ]

        bigquery_client.create_table(
            table
        )

        print(
            f"BigQuery table created: "
            f"{FULL_TABLE_ID}"
        )


# ---------------------------------------------------------
# PUB/SUB CALLBACK
# ---------------------------------------------------------

def callback(message):

    global received_count

    try:

        event = json.loads(
            message.data.decode("utf-8")
        )

        missing_fields = (
            REQUIRED_FIELDS - event.keys()
        )

        if missing_fields:

            print(
                "INVALID EVENT | "
                f"Missing fields: "
                f"{sorted(missing_fields)}"
            )

            message.nack()

            return

        row = {
            **event,
            "pubsub_message_id":
                message.message_id,
            "ingested_at":
                datetime.now(
                    timezone.utc
                ).isoformat(),
        }

        errors = (
            bigquery_client.insert_rows_json(
                FULL_TABLE_ID,
                [row],
                row_ids=[
                    event["event_id"]
                ],
            )
        )

        if errors:

            print("")
            print("BIGQUERY WRITE FAILED")
            print(errors)
            print("Message will be NACKed.")
            print("")

            message.nack()

            return

        # ACK only after BigQuery accepts the row.
        message.ack()

        with lock:

            received_count += 1

            current_number = (
                received_count
            )

        print(
            f"[{current_number:02d}"
            f"/{MAX_MESSAGES}] "
            f"{event['flight_id']} | "
            f"{event['origin_airport']}"
            f" -> "
            f"{event['destination_airport']} | "
            f"{event['event_type']:<20} | "
            f"BQ WRITE: SUCCESS | "
            f"ACK: SUCCESS"
        )

        if (
            current_number
            >= MAX_MESSAGES
        ):

            done.set()

    except Exception as error:

        print("")
        print(
            "STREAM PROCESSING FAILED"
        )
        print(
            type(error).__name__
        )
        print(error)
        print("")

        message.nack()


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------

def main():

    print("")
    print(
        "SKYFLOW PUB/SUB -> BIGQUERY"
    )
    print(
        "-----------------------------------------------"
    )
    print(
        f"Project:      {PROJECT_ID}"
    )
    print(
        f"Subscription: "
        f"{SUBSCRIPTION_ID}"
    )
    print(
        f"Destination:  "
        f"{FULL_TABLE_ID}"
    )
    print(
        f"Target:       "
        f"{MAX_MESSAGES} events"
    )
    print(
        "-----------------------------------------------"
    )
    print("")

    ensure_streaming_table()

    print("")
    print(
        "Waiting for live flight events..."
    )
    print("")

    streaming_pull_future = (
        subscriber.subscribe(
            subscription_path,
            callback=callback,
        )
    )

    completed = False
    interrupted = False

    try:

        completed = done.wait(
            timeout=
            WAIT_TIMEOUT_SECONDS
        )

        if not completed:

            print("")
            print(
                "STREAM TIMED OUT"
            )
            print(
                f"Events written: "
                f"{received_count}/"
                f"{MAX_MESSAGES}"
            )

    except KeyboardInterrupt:

        interrupted = True

        print("")
        print(
            "Streaming stopped manually."
        )

    finally:

        streaming_pull_future.cancel()

        try:

            streaming_pull_future.result()

        except Exception:

            pass

        subscriber.close()

    print("")
    print(
        "-----------------------------------------------"
    )

    if completed and not interrupted and received_count >= MAX_MESSAGES:

        print(
            "SKYFLOW STREAM -> "
            "BIGQUERY: SUCCESS"
        )

        print(
            f"Events written: "
            f"{received_count}"
        )

    else:

        print(
            "SKYFLOW STREAM -> "
            "BIGQUERY: INCOMPLETE"
        )

        print(
            f"Events written: "
            f"{received_count}"
        )

    print(
        "-----------------------------------------------"
    )
    print("")


    if interrupted:
        return 130
    return 0 if completed and received_count >= MAX_MESSAGES else 1


if __name__ == "__main__":
    sys.exit(main())
