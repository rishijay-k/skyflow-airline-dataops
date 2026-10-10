CREATE OR REPLACE VIEW
`skyflow-511113.skyflow_ops.streaming_airport_metrics`

AS

SELECT
    origin_airport,

    COUNT(*) AS total_live_events,

    COUNTIF(
        event_type = 'DEPARTURE_DELAYED'
    ) AS delayed_events,

    ROUND(
        100 * SAFE_DIVIDE(
            COUNTIF(
                event_type = 'DEPARTURE_DELAYED'
            ),
            COUNT(*)
        ),
        2
    ) AS delay_percentage,

    ROUND(
        AVG(
            TIMESTAMP_DIFF(
                ingested_at,
                event_timestamp,
                MILLISECOND
            )
        ) / 1000,
        3
    ) AS avg_ingestion_latency_seconds,

    MAX(ingested_at) AS latest_event_received

FROM
`skyflow-511113.skyflow_raw.flight_events_streaming`

GROUP BY
    origin_airport;
