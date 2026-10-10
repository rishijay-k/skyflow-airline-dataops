from pathlib import Path
from google.cloud import bigquery


PROJECT_ID = "skyflow-511113"
DATASET_ID = "skyflow_raw"
TABLE_ID = "flight_events"
LOCATION = "asia-south1"

SOURCE_FILE = Path("data/flight_events_1000.jsonl")

FULL_TABLE_ID = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"


SCHEMA = [
    bigquery.SchemaField("event_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("flight_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("origin_airport", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("destination_airport", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("event_type", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("event_timestamp", "TIMESTAMP", mode="REQUIRED"),
    bigquery.SchemaField("delay_minutes", "INTEGER", mode="REQUIRED"),
    bigquery.SchemaField("aircraft_type", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("flight_status", "STRING", mode="REQUIRED"),
]


def main():

    if not SOURCE_FILE.exists():
        raise FileNotFoundError(
            f"Source file not found: {SOURCE_FILE}"
        )

    client = bigquery.Client(
        project=PROJECT_ID,
        location=LOCATION
    )

    job_config = bigquery.LoadJobConfig(
        schema=SCHEMA,
        source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
    )

    print("")
    print("SKYFLOW BIGQUERY RAW LOADER")
    print("---------------------------")
    print(f"Project: {PROJECT_ID}")
    print(f"Dataset: {DATASET_ID}")
    print(f"Table: {TABLE_ID}")
    print(f"Location: {LOCATION}")
    print(f"Source: {SOURCE_FILE}")
    print("")
    print("Loading airline events...")

    with SOURCE_FILE.open("rb") as source_file:

        load_job = client.load_table_from_file(
            source_file,
            FULL_TABLE_ID,
            location=LOCATION,
            job_config=job_config,
        )

    load_job.result()

    table = client.get_table(FULL_TABLE_ID)

    print("")
    print("LOAD SUCCESSFUL")
    print("---------------------------")
    print(f"Rows loaded: {table.num_rows}")
    print(f"Columns: {len(table.schema)}")
    print(f"Destination: {FULL_TABLE_ID}")
    print("")


if __name__ == "__main__":
    main()
