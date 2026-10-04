variable "enable_workspace" {
  description = <<-EOT
    Set up the Google Workspace Admin SDK Reports API integration (Pathway B).

    Google Workspace supports two ingestion architectures:
      Pathway A (Native Cloud Audit Sharing): Configured in admin.google.com -> Account Settings
        -> Legal and compliance -> Sharing options -> Google Cloud Platform. Writes audit logs
        directly to Cloud Logging at the Organization level, streaming real-time to Pub/Sub via
        modules/log-export with zero polling.
      Pathway B (Admin SDK Reports API): Used when native sharing is disabled, or when directory
        enrichment scopes (admin.directory.user.readonly, admin.directory.group.readonly) or
        application-specific streams (Drive, Gmail, Vault) are needed.

    This module provisions the dedicated GCP service account for Pathway B and emits the exact
    client ID, OAuth scopes, and Abstract onboarding values. Domain-wide delegation itself must
    be granted by a Workspace SUPER ADMIN in admin.google.com -- there is no API for it.
  EOT
  type        = bool
  default     = false
}
variable "workspace_admin_email" {
  description = "A Google Workspace ADMIN user the service account impersonates. Domain-wide delegation acts as a real user; without a subject the Reports API returns 401. Goes into Abstract's Admin Email field."
  type        = string
  default     = ""
}
variable "workspace_service_account_id" {
  description = "Account ID for the Workspace connector service account. Deliberately separate from the Pub/Sub one -- domain-wide delegation is a much broader trust and should be revocable on its own."
  type        = string
  default     = "abstract-workspace-reader"
}
variable "workspace_app_groups" {
  description = <<-EOT
    Which Workspace applications to collect, by group. Individual application names also
    work here.

      identity      login, saml, token, user_accounts, context_aware_access
                    -- the answer to "who signed in", and what most customers actually mean
      admin         admin, groups, groups_enterprise, rules
      data          drive, gmail, calendar, keep, vault  -- gmail and drive are the volume monsters
      endpoint      chrome, mobile
      collaboration chat, meet, jamboard, gplus
      platform      access_transparency, gcp, data_studio

    Default is identity + admin: the high-signal control-plane set.
  EOT
  type        = list(string)
  default     = ["identity", "admin"]
}
variable "workspace_applications" {
  description = "Explicit application list, overriding workspace_app_groups. Valid: access_transparency, admin, calendar, chat, chrome, context_aware_access, data_studio, drive, gcp, gmail, gplus, groups, groups_enterprise, jamboard, keep, login, meet, mobile, rules, saml, token, user_accounts, vault"
  type        = list(string)
  default     = []
}

variable "log_project" {
  description = "Project owning the connector service account and the Admin SDK API enablement."
  type        = string
}

variable "acknowledge_high_volume" {
  description = "Required to include gmail or drive — on a large tenant they dwarf every other application combined."
  type        = bool
  default     = false
}

variable "include_directory_enrichment_scopes" {
  description = "Include Admin SDK Directory API scopes (admin.directory.user.readonly, admin.directory.group.readonly) for user identity and group enrichment (department, manager, org unit, group membership)."
  type        = bool
  default     = false
}
