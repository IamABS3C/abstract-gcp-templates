# Billing account audit log export to Abstract Security.
#
# Billing accounts sit outside the GCP resource hierarchy (organization, folders,
# projects do NOT capture them). An organization-wide aggregated sink will miss
# billing account events like IAM policy changes, budget updates, and project
# billing link changes.
#
# This deployment binds a dedicated Cloud Logging sink directly to the billing
# account and exports its audit logs into Pub/Sub in a dedicated logging project.

terraform {
  required_version = ">= 1.5"
  required_providers {
    google = { source = "hashicorp/google", version = "~> 6.0" }
  }
}

provider "google" {
  project = var.log_project
}

module "log_export" {
  source = "../../modules/log-export"

  sink_scope              = "billing_account"
  billing_account_id      = var.billing_account_id
  log_project             = var.log_project
  acknowledge_pilot_scope = false

  log_categories       = var.log_categories
  exclusions           = var.exclusions
  labels               = var.labels
  retention_days       = var.retention_days
  ack_deadline_seconds = var.ack_deadline_seconds
  topic_name           = var.topic_name
  subscription_name    = var.subscription_name
  sink_name            = var.sink_name
  service_account_id   = var.service_account_id
  custom_filter        = var.custom_filter
}
