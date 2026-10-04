# Abstract Security Normalization Parsers

Ingestion pipeline definitions for Abstract Security that parse, normalize, and enrich Google Cloud and Google Workspace telemetry streams into standard Elastic Common Schema (ECS) and Open Cybersecurity Schema Framework (OCSF) events.

## Available Parsers

| Parser | Telemetry Source | Description | Normalized Dataset |
|---|---|---|---|
| [`gcp-identity-auth.yml`](gcp-identity-auth.yml) | Google Cloud Audit Logs | Normalizes Cloud Identity/Workspace logins, Service Account impersonation (`iamcredentials`), Workload Identity Federation (`sts`), and static key usage | `gcp.identity_auth` |
| [`scc-findings.yml`](scc-findings.yml) | Security Command Center | Normalizes real-time security posture violations, threats, and vulnerability findings | `gcp.scc_findings` |
| [`workspace-reports.yml`](workspace-reports.yml) | Google Workspace Admin SDK Reports API | Normalizes user logins, token grants, admin actions, and SAML events | `google_workspace.audit` |

## Key Identity Enrichment Fields

The `gcp-identity-auth.yml` pipeline extracts critical security metadata from `protoPayload`:

- `user.email`: Authenticated principal email (user or service account).
- `source.ip`: Caller IP address (`protoPayload.requestMetadata.callerIp`).
- `user_agent.original`: Client agent string (`callerSuppliedUserAgent`).
- `gcp.iam.auth_mechanism`: Flagged as `static_service_account_key` when `serviceAccountKeyName` is present, or `workload_identity_federation` when `principalSubject` is present.
- `gcp.iam.service_account_key_name`: Full resource path of the private key used.
- `gcp.iam.delegation_chain`: Full service account impersonation trace.
- `event.outcome`: Evaluated as `success` or `failure` based on `status.code` or login event name.
