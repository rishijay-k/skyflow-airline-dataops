import sys
from google.cloud import bigquery


PROJECT_ID = "skyflow-511113"
LOCATION = "asia-south1"


QUERY = """
WITH raw_metrics AS (
    SELECT
        COUNT(*) AS raw_rows
    FROM `skyflow-511113.skyflow_raw.flight_events`
),

clean_metrics AS (
    SELECT
        COUNT(*) AS clean_rows,

        COUNT(DISTINCT event_id) AS unique_event_ids,

        COUNTIF(
            event_id IS NULL
            OR flight_id IS NULL
            OR origin_airport IS NULL
            OR destination_airport IS NULL
            OR event_type IS NULL
            OR event_timestamp IS NULL
        ) AS missing_critical_values,

        COUNTIF(
            origin_airport = destination_airport
        ) AS same_origin_destination,

        COUNTIF(
            delay_minutes < 0
        ) AS negative_delays,

        COUNTIF(
            flight_status !=
            CASE event_type
                WHEN 'FLIGHT_SCHEDULED' THEN 'SCHEDULED'
                WHEN 'GATE_ASSIGNED' THEN 'SCHEDULED'
                WHEN 'BOARDING_STARTED' THEN 'BOARDING'
                WHEN 'DEPARTURE_DELAYED' THEN 'DELAYED'
                WHEN 'DEPARTED' THEN 'DEPARTED'
                WHEN 'ARRIVED' THEN 'ARRIVED'
            END
        ) AS status_mismatches,

        COUNTIF(
            event_type NOT IN (
                'FLIGHT_SCHEDULED',
                'GATE_ASSIGNED',
                'BOARDING_STARTED',
                'DEPARTURE_DELAYED',
                'DEPARTED',
                'ARRIVED'
            )
        ) AS invalid_event_types

    FROM `skyflow-511113.skyflow_clean.flight_events_clean`
),

airport_metrics AS (
    SELECT
        COUNT(*) AS airport_metric_rows
    FROM `skyflow-511113.skyflow_curated.airport_operational_metrics`
),

route_metrics AS (
    SELECT
        COUNT(*) AS route_metric_rows
    FROM `skyflow-511113.skyflow_curated.route_operational_metrics`
)

SELECT *
FROM raw_metrics
CROSS JOIN clean_metrics
CROSS JOIN airport_metrics
CROSS JOIN route_metrics
"""


def print_check(name, passed, value):
    status = "PASS" if passed else "FAIL"

    print(
        f"{status:<4} | "
        f"{name:<35} | "
        f"{value}"
    )

    return passed


def main():

    client = bigquery.Client(
        project=PROJECT_ID,
        location=LOCATION
    )

    print("")
    print("SKYFLOW AUTOMATED DATA QUALITY")
    print("-----------------------------------------------")

    result = list(client.query(
        QUERY,
        location=LOCATION
    ).result())[0]

    checks = []

    checks.append(
        print_check(
            "RAW table contains data",
            result.raw_rows > 0,
            result.raw_rows
        )
    )

    checks.append(
        print_check(
            "RAW and CLEAN row counts match",
            result.raw_rows == result.clean_rows,
            f"{result.raw_rows} / {result.clean_rows}"
        )
    )

    checks.append(
        print_check(
            "Event IDs are unique",
            result.unique_event_ids == result.clean_rows,
            result.unique_event_ids
        )
    )

    checks.append(
        print_check(
            "Critical fields are complete",
            result.missing_critical_values == 0,
            result.missing_critical_values
        )
    )

    checks.append(
        print_check(
            "Routes have different airports",
            result.same_origin_destination == 0,
            result.same_origin_destination
        )
    )

    checks.append(
        print_check(
            "Delay values are non-negative",
            result.negative_delays == 0,
            result.negative_delays
        )
    )

    checks.append(
        print_check(
            "CLEAN statuses are consistent",
            result.status_mismatches == 0,
            result.status_mismatches
        )
    )

    checks.append(
        print_check(
            "Event types are valid",
            result.invalid_event_types == 0,
            result.invalid_event_types
        )
    )

    checks.append(
        print_check(
            "Airport metrics are complete",
            result.airport_metric_rows == 10,
            result.airport_metric_rows
        )
    )

    checks.append(
        print_check(
            "Route metrics exist",
            result.route_metric_rows > 0,
            result.route_metric_rows
        )
    )

    passed = sum(checks)
    total = len(checks)

    print("-----------------------------------------------")
    print(f"Checks passed: {passed}/{total}")

    if all(checks):

        print("")
        print("DATA QUALITY STATUS: PASS")
        print("SkyFlow data is safe to continue.")
        print("")

        sys.exit(0)

    else:

        print("")
        print("DATA QUALITY STATUS: FAIL")
        print("Pipeline should not continue.")
        print("")

        sys.exit(1)


if __name__ == "__main__":
    main()
