CREATE OR REPLACE VIEW
`skyflow-511113.skyflow_ops.pipeline_health`

AS

SELECT
    pipeline_name,

    COUNT(*) AS total_runs,

    COUNTIF(
        status = 'SUCCESS'
    ) AS successful_runs,

    COUNTIF(
        status = 'FAILED'
    ) AS failed_runs,

    ROUND(
        100 * SAFE_DIVIDE(
            COUNTIF(
                status = 'SUCCESS'
            ),
            COUNT(*)
        ),
        2
    ) AS success_rate_percentage,

    ROUND(
        AVG(duration_seconds),
        2
    ) AS avg_duration_seconds,

    MAX(finished_at)
        AS latest_run_at,

    ARRAY_AGG(
        status
        ORDER BY started_at DESC
        LIMIT 1
    )[OFFSET(0)]
        AS latest_status

FROM
`skyflow-511113.skyflow_ops.pipeline_runs`

GROUP BY
    pipeline_name;
