-- SkyFlow airport activity

SELECT
    origin_airport,
    COUNT(*) AS departures_or_events
FROM `skyflow-511113.skyflow_raw.flight_events`
GROUP BY origin_airport
ORDER BY departures_or_events DESC;
