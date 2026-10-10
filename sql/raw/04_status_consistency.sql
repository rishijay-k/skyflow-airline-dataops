SELECT
    COUNT(*) AS total_rows,

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
    ) AS inconsistent_status_rows

FROM `skyflow-511113.skyflow_raw.flight_events`;
