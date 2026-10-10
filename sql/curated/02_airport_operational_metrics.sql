-- =========================================================
-- SKYFLOW
-- CURATED AIRPORT OPERATIONAL METRICS
-- =========================================================

CREATE OR REPLACE TABLE
`skyflow-511113.skyflow_curated.airport_operational_metrics`

AS

SELECT
    origin_airport,

    COUNT(*) AS total_events,

    COUNTIF(is_delayed) AS delayed_events,

    ROUND(
        100 * SAFE_DIVIDE(
            COUNTIF(is_delayed),
            COUNT(*)
        ),
        2
    ) AS delayed_event_percentage,

    ROUND(
        AVG(
            IF(
                is_delayed,
                delay_minutes,
                NULL
            )
        ),
        2
    ) AS avg_delay_minutes_when_delayed,

    MAX(delay_minutes) AS maximum_delay_minutes,

    COUNT(DISTINCT destination_airport) AS destination_count,

    COUNTIF(status_was_corrected) AS corrected_status_events

FROM
    `skyflow-511113.skyflow_clean.flight_events_clean`

GROUP BY
    origin_airport;
