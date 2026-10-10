CREATE TABLE IF NOT EXISTS
`skyflow-511113.skyflow_ops.pipeline_runs`
(
    run_id STRING NOT NULL,
    pipeline_name STRING NOT NULL,
    run_type STRING NOT NULL,
    status STRING NOT NULL,

    started_at TIMESTAMP NOT NULL,
    finished_at TIMESTAMP,
    duration_seconds FLOAT64,

    records_processed INT64,

    error_message STRING,

    logged_at TIMESTAMP NOT NULL
);
