# Google Workspace / Cloud Identity audit logs.
#
# A SEPARATE PIPELINE — Workspace audit data comes from the Admin SDK Reports
# API and never touches Cloud Logging. No sink, no topic, no filter, at any
# scope, will ever collect it.
#
# This deployment creates the delegated service account and prints the exact
# values for the Admin console step, which Terraform cannot perform.

terraform {
  required_version = ">= 1.5"
  required_providers {
    google = { source = "hashicorp/google", version = "~> 6.0" }
  }
}

provider "google" {
  project = var.log_project
}

module "workspace" {
  source = "../../modules/workspace"

  enable_workspace             = true
  log_project                  = var.log_project
  workspace_admin_email        = var.workspace_admin_email
  workspace_app_groups         = var.workspace_app_groups
  workspace_applications       = var.workspace_applications
  workspace_service_account_id = var.workspace_service_account_id
  acknowledge_high_volume      = var.acknowledge_high_volume
}
