-- SkyFlow RAW event distribution

SELECT
    event_type,
    COUNT(*) AS total_events,
    ROUND(
        100 * COUNT(*) / SUM(COUNT(*)) OVER (),
        2
    ) AS percentage
FROM `skyflow-511113.skyflow_raw.flight_events`
GROUP BY event_type
ORDER BY total_events DESC;
