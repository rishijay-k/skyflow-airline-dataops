#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
umask 077
terraform init -input=false
terraform validate
if ! terraform state list | /usr/bin/grep -Fxq "google_bigquery_dataset.skyflow_raw"; then
  terraform import -input=false "google_bigquery_dataset.skyflow_raw" "projects/skyflow-511113/datasets/skyflow_raw"
fi
if ! terraform state list | /usr/bin/grep -Fxq "google_bigquery_dataset.skyflow_clean"; then
  terraform import -input=false "google_bigquery_dataset.skyflow_clean" "projects/skyflow-511113/datasets/skyflow_clean"
fi
if ! terraform state list | /usr/bin/grep -Fxq "google_bigquery_dataset.skyflow_curated"; then
  terraform import -input=false "google_bigquery_dataset.skyflow_curated" "projects/skyflow-511113/datasets/skyflow_curated"
fi
if ! terraform state list | /usr/bin/grep -Fxq "google_bigquery_dataset.skyflow_ops"; then
  terraform import -input=false "google_bigquery_dataset.skyflow_ops" "projects/skyflow-511113/datasets/skyflow_ops"
fi
if ! terraform state list | /usr/bin/grep -Fxq "google_pubsub_topic.flight_events"; then
  terraform import -input=false "google_pubsub_topic.flight_events" "projects/skyflow-511113/topics/skyflow-flight-events"
fi
if ! terraform state list | /usr/bin/grep -Fxq "google_pubsub_subscription.flight_events"; then
  terraform import -input=false "google_pubsub_subscription.flight_events" "projects/skyflow-511113/subscriptions/skyflow-flight-events-sub"
fi
