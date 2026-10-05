# Network Threat Telemetry Export to Abstract Security
#
# Combines:
#   - Cloud Armor WAF decisions (resource.type="http_load_balancer")
#   - Cloud IDS threat logs (logName:"ids.googleapis.com%2Fthreat")
#   - DNS queries (logName:"dns.googleapis.com%2Fdns_queries")
#   - Firewall rule decisions (logName:"compute.googleapis.com%2Ffirewall")
#
# Single aggregated sink routing network and perimeter security events
# directly to an Abstract Security Pub/Sub pull subscription.

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

  sink_scope              = var.sink_scope
  org_id                  = var.org_id
  folder_id               = var.folder_id
  log_project             = var.log_project
  sink_project            = var.sink_project
  acknowledge_pilot_scope = var.acknowledge_pilot_scope

  log_categories          = var.log_categories
  platform_log_filters    = var.platform_log_filters
  acknowledge_high_volume = var.acknowledge_high_volume
  audit_streams           = var.audit_streams

  topic_name                        = var.topic_name
  subscription_name                 = var.subscription_name
  sink_name                         = var.sink_name
  service_account_id                = var.service_account_id
  retention_days                    = var.retention_days
  ack_deadline_seconds              = var.ack_deadline_seconds
  enable_dead_letter                = var.enable_dead_letter
  dead_letter_max_delivery_attempts = var.dead_letter_max_delivery_attempts
  custom_filter                     = var.custom_filter
  exclusions                        = var.exclusions
  labels                            = var.labels
}

# Cost guard. The module itself only stops on extreme-tier categories; the defaults here
# (dns_queries, load_balancer) are high tier, so the plan also stops on those until the
# volume is acknowledged.
resource "terraform_data" "volume_acknowledgement" {
  lifecycle {
    precondition {
      condition     = var.acknowledge_high_volume || (module.log_export.volume_profile.high + module.log_export.volume_profile.extreme) == 0
      error_message = "High-volume categories selected (${join(", ", var.log_categories)}). They can dominate your bill.\nMeasure a 7-day baseline first. To proceed set acknowledge_high_volume = true (or -var acknowledge_high_volume=true)."
    }
  }
}
