-- =========================================================
-- SKYFLOW
-- RAW -> CLEAN TRANSFORMATION
-- =========================================================

CREATE OR REPLACE TABLE
`skyflow-511113.skyflow_clean.flight_events_clean`

PARTITION BY DATE(event_timestamp)

CLUSTER BY
    origin_airport,
    destination_airport,
    event_type

AS

SELECT
    event_id,
    flight_id,

    UPPER(TRIM(origin_airport)) AS origin_airport,
    UPPER(TRIM(destination_airport)) AS destination_airport,

    event_type,
    event_timestamp,

    delay_minutes,

    TRIM(aircraft_type) AS aircraft_type,

    -- Preserve what arrived from the source
    flight_status AS source_flight_status,

    -- Derive a trusted business status
    CASE event_type
        WHEN 'FLIGHT_SCHEDULED' THEN 'SCHEDULED'
        WHEN 'GATE_ASSIGNED' THEN 'SCHEDULED'
        WHEN 'BOARDING_STARTED' THEN 'BOARDING'
        WHEN 'DEPARTURE_DELAYED' THEN 'DELAYED'
        WHEN 'DEPARTED' THEN 'DEPARTED'
        WHEN 'ARRIVED' THEN 'ARRIVED'
    END AS flight_status,

    CONCAT(
        UPPER(TRIM(origin_airport)),
        '-',
        UPPER(TRIM(destination_airport))
    ) AS route,

    event_type = 'DEPARTURE_DELAYED' AS is_delayed,

    flight_status !=
        CASE event_type
            WHEN 'FLIGHT_SCHEDULED' THEN 'SCHEDULED'
            WHEN 'GATE_ASSIGNED' THEN 'SCHEDULED'
            WHEN 'BOARDING_STARTED' THEN 'BOARDING'
            WHEN 'DEPARTURE_DELAYED' THEN 'DELAYED'
            WHEN 'DEPARTED' THEN 'DEPARTED'
            WHEN 'ARRIVED' THEN 'ARRIVED'
        END
        AS status_was_corrected

FROM
    `skyflow-511113.skyflow_raw.flight_events`

WHERE
    event_id IS NOT NULL
    AND flight_id IS NOT NULL
    AND origin_airport IS NOT NULL
    AND destination_airport IS NOT NULL
    AND origin_airport != destination_airport
    AND delay_minutes >= 0;
