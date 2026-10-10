#!/bin/bash

set -euo pipefail

PROJECT_ID="skyflow-511113"
LOCATION="asia-south1"

START_TIME=$(date +%s)

echo ""
echo "=================================================="
echo "SKYFLOW BATCH PIPELINE"
echo "=================================================="
echo "Project:  ${PROJECT_ID}"
echo "Location: ${LOCATION}"
echo "Started:  $(date)"
echo "=================================================="
echo ""


echo "[1/6] Generating synthetic airline events..."
python src/generator/generate_flight_events.py

echo ""
echo "[2/6] Loading events into BigQuery RAW..."
python src/ingestion/load_raw_events.py

echo ""
echo "[3/6] Building CLEAN layer..."
bq query \
  --location="${LOCATION}" \
  --use_legacy_sql=false \
  < sql/clean/01_create_flight_events_clean.sql

echo ""
echo "[4/6] Building CURATED route metrics..."
bq query \
  --location="${LOCATION}" \
  --use_legacy_sql=false \
  < sql/curated/01_route_operational_metrics.sql

echo ""
echo "[5/6] Building CURATED airport metrics..."
bq query \
  --location="${LOCATION}" \
  --use_legacy_sql=false \
  < sql/curated/02_airport_operational_metrics.sql

echo ""
echo "[6/6] Running automated data-quality gate..."
python src/quality/run_data_quality.py


END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

echo ""
echo "=================================================="
echo "SKYFLOW BATCH PIPELINE: SUCCESS"
echo "=================================================="
echo "RAW:       skyflow_raw.flight_events"
echo "CLEAN:     skyflow_clean.flight_events_clean"
echo "CURATED:   route_operational_metrics"
echo "CURATED:   airport_operational_metrics"
echo "DQ STATUS: PASS"
echo "Duration:  ${DURATION} seconds"
echo "Finished:  $(date)"
echo "=================================================="
echo ""
