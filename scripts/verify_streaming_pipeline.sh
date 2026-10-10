#!/bin/bash

set -euo pipefail

PROJECT_ID="skyflow-511113"
LOCATION="asia-south1"

TOPIC="skyflow-flight-events"
SUBSCRIPTION="skyflow-flight-events-sub"

TABLE="skyflow-511113.skyflow_raw.flight_events_streaming"

LOG_FILE="logs/streaming_verification_consumer.log"

echo ""
echo "=================================================="
echo "SKYFLOW STREAMING PIPELINE VERIFICATION"
echo "=================================================="
echo ""

echo "[1/7] Checking GCP project..."

CURRENT_PROJECT=$(gcloud config get-value project 2>/dev/null)

if [ "$CURRENT_PROJECT" != "$PROJECT_ID" ]; then
    echo "FAIL: Wrong GCP project."
    echo "Expected: $PROJECT_ID"
    echo "Found:    $CURRENT_PROJECT"
    exit 1
fi

echo "PASS: $CURRENT_PROJECT"
echo ""


echo "[2/7] Checking Pub/Sub topic..."

gcloud pubsub topics describe "$TOPIC" \
    --project="$PROJECT_ID" \
    >/dev/null

echo "PASS: $TOPIC"
echo ""


echo "[3/7] Checking Pub/Sub subscription..."

gcloud pubsub subscriptions describe "$SUBSCRIPTION" \
    --project="$PROJECT_ID" \
    >/dev/null

echo "PASS: $SUBSCRIPTION"
echo ""


echo "[4/7] Reading current BigQuery row count..."

BEFORE_COUNT=$(bq query \
    --location="$LOCATION" \
    --use_legacy_sql=false \
    --format=csv \
    "SELECT COUNT(*) AS total
     FROM \`$TABLE\`" \
    | tail -1)

echo "Rows before test: $BEFORE_COUNT"
echo ""


echo "[5/7] Starting streaming consumer..."

mkdir -p logs

python src/streaming/stream_to_bigquery.py \
    > "$LOG_FILE" 2>&1 &

CONSUMER_PID=$!

sleep 4

echo "Consumer PID: $CONSUMER_PID"
echo ""


echo "[6/7] Publishing 20 live airline events..."

python src/streaming/publish_live_events.py

echo ""
echo "Waiting for consumer to finish..."

wait "$CONSUMER_PID"

echo ""
echo "Consumer completed."
echo ""


echo "[7/7] Validating BigQuery results..."

AFTER_COUNT=$(bq query \
    --location="$LOCATION" \
    --use_legacy_sql=false \
    --format=csv \
    "SELECT COUNT(*) AS total
     FROM \`$TABLE\`" \
    | tail -1)

NEW_ROWS=$((AFTER_COUNT - BEFORE_COUNT))

MISSING_IDS=$(bq query \
    --location="$LOCATION" \
    --use_legacy_sql=false \
    --format=csv \
    "SELECT COUNT(*) AS total
     FROM \`$TABLE\`
     WHERE pubsub_message_id IS NULL" \
    | tail -1)

echo ""
echo "Rows before:        $BEFORE_COUNT"
echo "Rows after:         $AFTER_COUNT"
echo "New rows detected:  $NEW_ROWS"
echo "Missing message IDs:$MISSING_IDS"
echo ""


if [ "$NEW_ROWS" -lt 20 ]; then

    echo "=================================================="
    echo "SKYFLOW STREAMING VERIFICATION: FAIL"
    echo "Expected at least 20 new BigQuery rows."
    echo "=================================================="

    exit 1

fi


if [ "$MISSING_IDS" -ne 0 ]; then

    echo "=================================================="
    echo "SKYFLOW STREAMING VERIFICATION: FAIL"
    echo "Some rows do not contain Pub/Sub message IDs."
    echo "=================================================="

    exit 1

fi


echo "=================================================="
echo "SKYFLOW STREAMING VERIFICATION: SUCCESS"
echo "=================================================="
echo "Producer:        PASS"
echo "Pub/Sub topic:   PASS"
echo "Subscription:    PASS"
echo "Consumer:        PASS"
echo "BigQuery writes: PASS"
echo "Traceability:    PASS"
echo "New rows:        $NEW_ROWS"
echo "=================================================="
echo ""
echo "Consumer log:"
echo "$LOG_FILE"
echo ""
