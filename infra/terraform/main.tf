# __generated__ by Terraform
# Please review these resources and move them into your main configuration files.

# __generated__ by Terraform
resource "google_bigquery_dataset" "skyflow_curated" {
  lifecycle {
    prevent_destroy = true
  }
  dataset_id                      = "skyflow_curated"
  default_partition_expiration_ms = 0
  delete_contents_on_destroy      = false
  deletion_policy                 = "DELETE"
  description                     = "SkyFlow business-ready airline operational metrics"
  friendly_name                   = null
  is_case_insensitive             = false
  labels                          = {}
  location                        = "asia-south1"
  max_time_travel_hours           = "168"
  project                         = "skyflow-511113"
  resource_tags                   = {}
  access {
    domain         = null
    group_by_email = null
    iam_member     = null
    role           = "OWNER"
    special_group  = "projectOwners"
    user_by_email  = null
  }
  access {
    domain         = null
    group_by_email = null
    iam_member     = null
    role           = "OWNER"
    special_group  = null
    user_by_email  = var.dataset_owner_email
  }
  access {
    domain         = null
    group_by_email = null
    iam_member     = null
    role           = "READER"
    special_group  = "projectReaders"
    user_by_email  = null
  }
  access {
    domain         = null
    group_by_email = null
    iam_member     = null
    role           = "WRITER"
    special_group  = "projectWriters"
    user_by_email  = null
  }
}

# __generated__ by Terraform
resource "google_bigquery_dataset" "skyflow_ops" {
  lifecycle {
    prevent_destroy = true
  }
  dataset_id                      = "skyflow_ops"
  default_partition_expiration_ms = 0
  delete_contents_on_destroy      = false
  deletion_policy                 = "DELETE"
  description                     = "SkyFlow operational monitoring and streaming metrics"
  friendly_name                   = null
  is_case_insensitive             = false
  labels                          = {}
  location                        = "asia-south1"
  max_time_travel_hours           = "168"
  project                         = "skyflow-511113"
  resource_tags                   = {}
  access {
    domain         = null
    group_by_email = null
    iam_member     = null
    role           = "OWNER"
    special_group  = "projectOwners"
    user_by_email  = null
  }
  access {
    domain         = null
    group_by_email = null
    iam_member     = null
    role           = "OWNER"
    special_group  = null
    user_by_email  = var.dataset_owner_email
  }
  access {
    domain         = null
    group_by_email = null
    iam_member     = null
    role           = "READER"
    special_group  = "projectReaders"
    user_by_email  = null
  }
  access {
    domain         = null
    group_by_email = null
    iam_member     = null
    role           = "WRITER"
    special_group  = "projectWriters"
    user_by_email  = null
  }
}

# __generated__ by Terraform
resource "google_bigquery_dataset" "skyflow_clean" {
  lifecycle {
    prevent_destroy = true
  }
  dataset_id                      = "skyflow_clean"
  default_partition_expiration_ms = 0
  delete_contents_on_destroy      = false
  deletion_policy                 = "DELETE"
  description                     = "SkyFlow validated and standardized airline events"
  friendly_name                   = null
  is_case_insensitive             = false
  labels                          = {}
  location                        = "asia-south1"
  max_time_travel_hours           = "168"
  project                         = "skyflow-511113"
  resource_tags                   = {}
  access {
    domain         = null
    group_by_email = null
    iam_member     = null
    role           = "OWNER"
    special_group  = "projectOwners"
    user_by_email  = null
  }
  access {
    domain         = null
    group_by_email = null
    iam_member     = null
    role           = "OWNER"
    special_group  = null
    user_by_email  = var.dataset_owner_email
  }
  access {
    domain         = null
    group_by_email = null
    iam_member     = null
    role           = "READER"
    special_group  = "projectReaders"
    user_by_email  = null
  }
  access {
    domain         = null
    group_by_email = null
    iam_member     = null
    role           = "WRITER"
    special_group  = "projectWriters"
    user_by_email  = null
  }
}

# __generated__ by Terraform
resource "google_bigquery_dataset" "skyflow_raw" {
  lifecycle {
    prevent_destroy = true
  }
  dataset_id                      = "skyflow_raw"
  default_partition_expiration_ms = 0
  delete_contents_on_destroy      = false
  deletion_policy                 = "DELETE"
  description                     = "SkyFlow raw airline operational events"
  friendly_name                   = null
  is_case_insensitive             = false
  labels                          = {}
  location                        = "asia-south1"
  max_time_travel_hours           = "168"
  project                         = "skyflow-511113"
  resource_tags                   = {}
  access {
    domain         = null
    group_by_email = null
    iam_member     = null
    role           = "OWNER"
    special_group  = "projectOwners"
    user_by_email  = null
  }
  access {
    domain         = null
    group_by_email = null
    iam_member     = null
    role           = "OWNER"
    special_group  = null
    user_by_email  = var.dataset_owner_email
  }
  access {
    domain         = null
    group_by_email = null
    iam_member     = null
    role           = "READER"
    special_group  = "projectReaders"
    user_by_email  = null
  }
  access {
    domain         = null
    group_by_email = null
    iam_member     = null
    role           = "WRITER"
    special_group  = "projectWriters"
    user_by_email  = null
  }
}

# __generated__ by Terraform from "projects/skyflow-511113/topics/skyflow-flight-events"
resource "google_pubsub_topic" "flight_events" {
  lifecycle {
    prevent_destroy = true
  }
  deletion_policy            = "DELETE"
  kms_key_name               = null
  labels                     = {}
  message_retention_duration = null
  name                       = "skyflow-flight-events"
  project                    = "skyflow-511113"
  tags                       = null
}

# __generated__ by Terraform from "projects/skyflow-511113/subscriptions/skyflow-flight-events-sub"
resource "google_pubsub_subscription" "flight_events" {
  lifecycle {
    prevent_destroy = true
  }
  ack_deadline_seconds         = 30
  deletion_policy              = "DELETE"
  enable_exactly_once_delivery = false
  enable_message_ordering      = false
  filter                       = null
  labels                       = {}
  message_retention_duration   = "604800s"
  name                         = "skyflow-flight-events-sub"
  project                      = "skyflow-511113"
  retain_acked_messages        = false
  tags                         = null
  topic                        = google_pubsub_topic.flight_events.id
  expiration_policy {
    ttl = "2678400s"
  }
}
