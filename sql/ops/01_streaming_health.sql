CREATE OR REPLACE VIEW
`skyflow-511113.skyflow_ops.streaming_health`

AS

SELECT
    COUNT(*) AS total_streamed_events,

    COUNT(DISTINCT event_id) AS unique_events,

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
    ) AS delayed_event_percentage,

    ROUND(
        AVG(
            IF(
                event_type = 'DEPARTURE_DELAYED',
                delay_minutes,
                NULL
            )
        ),
        2
    ) AS avg_delay_minutes_when_delayed,

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

    COUNTIF(
        ingested_at >=
        TIMESTAMP_SUB(
            CURRENT_TIMESTAMP(),
            INTERVAL 5 MINUTE
        )
    ) AS events_last_5_minutes,

    MIN(ingested_at) AS first_ingested_at,

    MAX(ingested_at) AS latest_ingested_at

FROM
`skyflow-511113.skyflow_raw.flight_events_streaming`;
