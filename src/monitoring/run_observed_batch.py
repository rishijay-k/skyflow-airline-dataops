import subprocess
import sys
import uuid

from datetime import datetime, timezone

from google.cloud import bigquery


PROJECT_ID = "skyflow-511113"
LOCATION = "asia-south1"

PIPELINE_RUNS_TABLE = (
    "skyflow-511113."
    "skyflow_ops."
    "pipeline_runs"
)


def utc_now():
    return datetime.now(
        timezone.utc
    )


def get_record_count(client):

    query = """
    SELECT COUNT(*) AS total_rows
    FROM
    `skyflow-511113.skyflow_raw.flight_events`
    """

    result = list(
        client.query(
            query,
            location=LOCATION
        ).result()
    )

    return result[0].total_rows


def log_run(
    client,
    run_id,
    status,
    started_at,
    finished_at,
    records_processed,
    error_message
):

    duration = (
        finished_at
        - started_at
    ).total_seconds()

    row = {
        "run_id": run_id,
        "pipeline_name":
            "skyflow_batch_pipeline",
        "run_type":
            "BATCH",
        "status":
            status,
        "started_at":
            started_at.isoformat(),
        "finished_at":
            finished_at.isoformat(),
        "duration_seconds":
            duration,
        "records_processed":
            records_processed,
        "error_message":
            error_message,
        "logged_at":
            utc_now().isoformat(),
    }

    errors = (
        client.insert_rows_json(
            PIPELINE_RUNS_TABLE,
            [row]
        )
    )

    if errors:

        raise RuntimeError(
            f"Observability logging failed: "
            f"{errors}"
        )


def main():

    client = bigquery.Client(
        project=PROJECT_ID,
        location=LOCATION
    )

    run_id = str(
        uuid.uuid4()
    )

    started_at = utc_now()

    status = "FAILED"
    records_processed = 0
    error_message = None

    print("")
    print(
        "SKYFLOW OBSERVED BATCH RUN"
    )
    print(
        "------------------------------------"
    )
    print(
        f"Run ID: {run_id}"
    )
    print(
        f"Started: {started_at}"
    )
    print(
        "------------------------------------"
    )
    print("")

    try:

        subprocess.run(
            [
                "bash",
                "scripts/run_batch_pipeline.sh"
            ],
            check=True
        )

        records_processed = (
            get_record_count(
                client
            )
        )

        status = "SUCCESS"

    except Exception as error:

        error_message = (
            f"{type(error).__name__}: "
            f"{error}"
        )

        print("")
        print(
            "PIPELINE EXECUTION FAILED"
        )
        print(error_message)
        print("")

    finally:

        finished_at = utc_now()

        log_run(
            client=client,
            run_id=run_id,
            status=status,
            started_at=started_at,
            finished_at=finished_at,
            records_processed=
                records_processed,
            error_message=
                error_message
        )

    print("")
    print(
        "------------------------------------"
    )
    print(
        f"Run status: {status}"
    )
    print(
        f"Records processed: "
        f"{records_processed}"
    )
    print(
        "Observability record: SAVED"
    )
    print(
        "------------------------------------"
    )
    print("")

    if status != "SUCCESS":

        sys.exit(1)


if __name__ == "__main__":
    main()
