# Abstract Security Normalization Parsers

Configuration-level parsers for Abstract Security GCP Pub/Sub configurations.

**Audit logs need no parser from this folder.** Abstract's managed GCP Pub/Sub parser already parses Cloud Audit Logs, including logins, service-account impersonation, Workload Identity Federation and key use. A configuration-level parser **replaces** the managed parser, so never install one of these on the configuration that reads `abstract-audit-logs-sub`: audit logs would stop being stored. Each parser here goes only on a separate configuration that reads its own feed's subscription.

## Available Parsers

| Parser | Install on | Status |
|---|---|---|
| [`cloud-asset-inventory.yml`](cloud-asset-inventory.yml) | The configuration for `abstract-asset-changes-sub` (deployment 07) | See [ABSTRACT-INTEGRATION.md](../docs/ABSTRACT-INTEGRATION.md#asset-inventory--resource-and-iam-policy-changes) |
| [`scc-findings.yml`](scc-findings.yml) | The configuration for `abstract-audit-logs-sub-scc` (deployment 06) | Preview: writes some fields Abstract does not have yet |
| [`workspace-reports.yml`](workspace-reports.yml) | Do not install | Workspace logs come from Abstract's Google Workspace integration, which has its own managed parser |
