-- =========================================================
-- SKYFLOW
-- RAW AIRLINE EVENT VALIDATION
--
-- Project: skyflow-511113
-- Dataset: skyflow_raw
-- Table: flight_events
-- =========================================================

SELECT
    COUNT(*) AS total_rows,

    COUNT(DISTINCT event_id) AS unique_event_ids,

    COUNT(*) - COUNT(DISTINCT event_id) AS duplicate_event_ids,

    COUNTIF(event_id IS NULL) AS missing_event_ids,

    COUNTIF(flight_id IS NULL) AS missing_flight_ids,

    COUNTIF(origin_airport IS NULL) AS missing_origins,

    COUNTIF(destination_airport IS NULL) AS missing_destinations,

    COUNTIF(origin_airport = destination_airport) AS same_origin_destination,

    COUNTIF(
        origin_airport NOT IN (
            'AMS', 'JFK', 'LHR', 'DEL', 'CDG',
            'FRA', 'DXB', 'SIN', 'BOM', 'BLR'
        )
    ) AS invalid_origin_airports,

    COUNTIF(
        destination_airport NOT IN (
            'AMS', 'JFK', 'LHR', 'DEL', 'CDG',
            'FRA', 'DXB', 'SIN', 'BOM', 'BLR'
        )
    ) AS invalid_destination_airports,

    COUNTIF(
        event_type NOT IN (
            'FLIGHT_SCHEDULED',
            'GATE_ASSIGNED',
            'BOARDING_STARTED',
            'DEPARTURE_DELAYED',
            'DEPARTED',
            'ARRIVED'
        )
    ) AS invalid_event_types,

    COUNTIF(delay_minutes < 0) AS negative_delays,

    COUNTIF(
        event_type != 'DEPARTURE_DELAYED'
        AND delay_minutes > 0
    ) AS unexpected_delay_values,

    COUNTIF(
        event_type = 'DEPARTURE_DELAYED'
        AND delay_minutes <= 0
    ) AS invalid_delayed_events

FROM `skyflow-511113.skyflow_raw.flight_events`;
