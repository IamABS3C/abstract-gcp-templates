#!/usr/bin/env python3
"""Build the Ultimate Architecture & Diagnostics Explorer SPA for Abstract GCP Templates.

Generates docs/architecture-explorer.html as a self-contained, enterprise-grade,
interactive web application featuring all 16 scenarios, dynamic multi-tab inspection,
SVG/PNG diagram viewer with zoom/pan, copyable CLI diagnostics, schema mappings,
and Terraform configurations.
"""

import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
DOCS_DIR = ROOT / "docs"
OUT_HTML = DOCS_DIR / "architecture-explorer.html"
BRAND_DIR = ROOT / "brand"

# Load SVG logo mark for inline embedding (ensures 100% offline/local reliability)
LOGO_SVG_PATH = BRAND_DIR / "abstract-logo-mark.svg"
LOGO_SVG = LOGO_SVG_PATH.read_text(encoding="utf-8") if LOGO_SVG_PATH.exists() else ""

SCENARIOS_DATA = {
    "01-logging-project": {
        "id": "01-logging-project",
        "category": "Core Hub & Infrastructure",
        "num": "01",
        "title": "Scenario 01 · Dedicated Central Logging Project Hub",
        "subtitle": "Centralized telemetry repository · Least-privilege reader identity · Quota isolation · CMEK encryption",
        "chips": [
            {"text": "CORE INFRASTRUCTURE", "tone": "teal"},
            {"text": "KEYLESS WIF", "tone": "cyan"},
            {"text": "< 120MS P99", "tone": "amber"},
            {"text": "SEVEN-DAY BUFFER", "tone": "pink"}
        ],
        "drawio": "diagrams/01-logging-project.drawio",
        "imgPng": "../diagrams/01-logging-project.png",
        "imgSvg": "../diagrams/01-logging-project.svg",
        "specs": {
            "logNames": "Administrative boundary · Pub/Sub transport · logging.googleapis.com",
            "protocol": "Google Cloud Pub/Sub Streaming Pull gRPC (Port 443 TLS 1.3)",
            "latency": "< 120ms P99 end-to-end telemetry transit",
            "throughput": "Absorbs up to 100,000+ eps peak ingest per subscription",
            "durability": "7-day unacknowledged retention + Dead Letter Topic buffer"
        },
        "topology": [
            "Organization and Folders contain distributed business workload projects.",
            "Dedicated Logging Project ('log_project') acts as an isolated administrative boundary.",
            "Cloud Logging and Pub/Sub APIs enabled exclusively within the logging hub.",
            "Pub/Sub Topic ('abstract-audit-logs') and Pull Subscription receive all routed telemetry.",
            "Abstract Service Account reader holds least-privilege 'roles/pubsub.subscriber' ONLY.",
            "Abstract Security Composable SIEM pulls streaming telemetry into Pipelines, Detections, LakeVilla, and AI-SecOps."
        ],
        "diagnostics": {
            "trapTitle": "THE #1 TRAP: Service Account Over-Privileging & Destination Quota Depletion",
            "trapDesc": "Pub/Sub publish quota is consumed in the DESTINATION logging project, NOT in source projects. Workload teams must never be granted IAM rights in the logging project. The Abstract reader service account requires 'roles/pubsub.subscriber' ONLY.",
            "trapFix": "gcloud projects add-iam-policy-binding $LOG_PROJECT --member=\"serviceAccount:abstract-gcp-reader@$LOG_PROJECT.iam.gserviceaccount.com\" --role=\"roles/pubsub.subscriber\"",
            "steps": [
                {
                    "num": 1,
                    "title": "Verify Required GCP APIs Activated in Logging Project",
                    "cmd": "gcloud services list --project=$LOG_PROJECT --filter=\"name:(pubsub.googleapis.com OR logging.googleapis.com)\""
                },
                {
                    "num": 2,
                    "title": "Verify Destination Pub/Sub Topic and KMS Key Status",
                    "cmd": "gcloud pubsub topics describe abstract-audit-logs --project=$LOG_PROJECT --format=\"yaml(name,kmsKeyName)\""
                },
                {
                    "num": 3,
                    "title": "Verify Subscription Expiration and Dead-Letter Configuration",
                    "cmd": "gcloud pubsub subscriptions describe abstract-audit-logs-sub --project=$LOG_PROJECT --format=\"yaml(ackDeadlineSeconds,expirationPolicy,deadLetterPolicy)\""
                },
                {
                    "num": 4,
                    "title": "Verify Abstract Reader Service Account Least-Privilege Role",
                    "cmd": "gcloud pubsub subscriptions get-iam-policy abstract-audit-logs-sub --project=$LOG_PROJECT --flatten=\"bindings[].members\" --filter=\"bindings.role:roles/pubsub.subscriber\""
                },
                {
                    "num": 5,
                    "title": "Perform Live Non-Destructive Subscription Pull Test",
                    "cmd": "gcloud pubsub subscriptions pull abstract-audit-logs-sub --project=$LOG_PROJECT --auto-ack --limit=1"
                }
            ]
        },
        "schema": {
            "fields": [
                {"raw": "timestamp", "acs": "@timestamp", "desc": "Event generation timestamp in ISO 8601 UTC format", "util": "Temporal sliding correlation & timeseries indexing"},
                {"raw": "protoPayload.serviceName", "acs": "event.dataset", "desc": "Target GCP service emitting the log event", "util": "Service-tier categorization & blast radius analytics"},
                {"raw": "protoPayload.methodName", "acs": "event.action", "desc": "Exact RPC method executed during caller mutation", "util": "Privilege escalation and unauthorized change detection"},
                {"raw": "protoPayload.authenticationInfo.principalEmail", "acs": "user.email", "desc": "Identity email of human user or service account", "util": "User & Entity Behavior Analytics (UEBA)"},
                {"raw": "protoPayload.requestMetadata.callerIp", "acs": "source.ip", "desc": "Originating IPv4 or IPv6 address of caller", "util": "GeoIP threat intelligence, Tor exit, VPN detection"}
            ],
            "ruleTitle": "Actionable SIEM Rule: Critical Service Account Key Creation Outside Bastion",
            "ruleKql": "vendor: GCP and event.action: \"google.iam.admin.v1.CreateServiceAccountKey\" and not (source.ip in [\"10.0.0.0/8\", \"192.168.0.0/16\"]) | score risk_score=95",
            "ruleSql": "SELECT timestamp, protoPayload.authenticationInfo.principalEmail, protoPayload.requestMetadata.callerIp\nFROM `logging_project.audit_logs.cloudaudit_googleapis_com_activity`\nWHERE protoPayload.methodName = 'google.iam.admin.v1.CreateServiceAccountKey'\n  AND NOT NET.IP_TRUNC(NET.SAFE_IP_FROM_STRING(protoPayload.requestMetadata.callerIp), 16) = b\"\\xc0\\xa8\\x00\\x00\"",
            "mitre": ["T1098 - Account Manipulation", "T1078.004 - Cloud Accounts", "T1562 - Impair Defenses"]
        },
        "terraform": """module "logging_project" {
  source = "../../modules/log-export"

  sink_scope         = "project"
  create_project     = true
  project_id         = var.log_project
  org_id             = var.org_id
  billing_account_id = var.billing_account_id

  topic_name         = "abstract-audit-logs"
  subscription_name  = "abstract-audit-logs-sub"
  service_account_id = "abstract-gcp-reader"

  labels = {
    managed_by = "opentofu"
    security   = "abstract"
    tier       = "telemetry-hub"
  }
}"""
    },

    "02-audit-logs-organization": {
        "id": "02-audit-logs-organization",
        "category": "Core Hub & Infrastructure",
        "num": "02",
        "title": "Scenario 02 · Organization-Wide Aggregated Audit Telemetry",
        "subtitle": "Admin Activity & System Events · Complete resource hierarchy capture · --include-children cascade",
        "chips": [
            {"text": "ORG-WIDE AUDIT", "tone": "teal"},
            {"text": "CASCADE INCLUDED", "tone": "cyan"},
            {"text": "< 100MS P99", "tone": "amber"},
            {"text": "ZERO-LOSS DURABILITY", "tone": "pink"}
        ],
        "drawio": "diagrams/02-audit-logs-organization.drawio",
        "imgPng": "../diagrams/02-audit-logs-organization.png",
        "imgSvg": "../diagrams/02-audit-logs-organization.svg",
        "specs": {
            "logNames": "cloudaudit.googleapis.com/activity, system_event, policy",
            "protocol": "Log Router aggregated sink -> Pub/Sub streaming gRPC",
            "latency": "< 100ms P99 from RPC invocation to Pub/Sub ingest",
            "throughput": "Up to 50,000 eps aggregated across enterprise org",
            "durability": "At-least-once guaranteed delivery, zero silent drop"
        },
        "topology": [
            "All current and future projects in the Organization hierarchy emit Cloud Audit Logs.",
            "Log Router Aggregated Sink at organizations/$ORG_ID intercepts all child telemetry.",
            "--include-children flag ensures new folders and projects are automatically monitored.",
            "Sink routes events into Pub/Sub topic 'abstract-audit-logs' in the central logging project.",
            "Abstract Security pull subscription ingests real-time events for continuous compliance."
        ],
        "diagnostics": {
            "trapTitle": "THE #1 TRAP: Silent Sink Ingestion Drop (Zero Events in Pub/Sub)",
            "trapDesc": "When creating an aggregated sink, GCP provisions a unique service account (service-org-ID@gcp-sa-logging.iam.gserviceaccount.com). It has ZERO permissions by default! Without roles/pubsub.publisher on the destination topic, logs are dropped silently with NO console error!",
            "trapFix": "WRITER=$(gcloud logging sinks describe abstract-org-sink --organization=$ORG_ID --format=\"value(writerIdentity)\")\ngcloud pubsub topics add-iam-policy-binding abstract-audit-logs --project=$LOG_PROJECT --member=\"$WRITER\" --role=\"roles/pubsub.publisher\"",
            "steps": [
                {
                    "num": 1,
                    "title": "Verify Organization Sink Configuration and Children Inclusion",
                    "cmd": "gcloud logging sinks describe abstract-org-sink --organization=$ORG_ID --format=\"yaml(name,destination,includeChildren,writerIdentity,filter)\""
                },
                {
                    "num": 2,
                    "title": "Extract Sink Unique Writer Identity Service Account",
                    "cmd": "gcloud logging sinks describe abstract-org-sink --organization=$ORG_ID --format=\"value(writerIdentity)\""
                },
                {
                    "num": 3,
                    "title": "Verify Topic Publisher IAM Binding on Destination Topic",
                    "cmd": "gcloud pubsub topics get-iam-policy abstract-audit-logs --project=$LOG_PROJECT --flatten=\"bindings[].members\" --filter=\"bindings.role:roles/pubsub.publisher\""
                },
                {
                    "num": 4,
                    "title": "Check Cloud Monitoring for Sink Delivery Errors",
                    "cmd": "gcloud monitoring metrics-scopes list --project=$LOG_PROJECT"
                },
                {
                    "num": 5,
                    "title": "Pull Live Message to Verify End-to-End Delivery",
                    "cmd": "gcloud pubsub subscriptions pull abstract-audit-logs-sub --project=$LOG_PROJECT --auto-ack --limit=1"
                }
            ]
        },
        "schema": {
            "fields": [
                {"raw": "protoPayload.serviceData.policyDelta", "acs": "gcp.audit.policy_delta", "desc": "IAM roles granted or revoked during SetIamPolicy", "util": "Critical: Immediate detection of backdoor admin grants"},
                {"raw": "protoPayload.status.code", "acs": "event.outcome", "desc": "gRPC return status code (0 = SUCCESS, 7 = PERMISSION_DENIED)", "util": "Brute force and reconnaissance pattern discovery"},
                {"raw": "resource.labels.project_id", "acs": "cloud.project.id", "desc": "Originating GCP project identifier in organization", "util": "Tenant partitioning and blast radius isolation"},
                {"raw": "protoPayload.requestMetadata.callerSuppliedUserAgent", "acs": "user_agent.original", "desc": "Client HTTP/gRPC user-agent string", "util": "Automated attack tool and script signature matching"}
            ],
            "ruleTitle": "Actionable SIEM Rule: Organization-Level IAM Policy Tampering",
            "ruleKql": "vendor: GCP and event.action: \"SetIamPolicy\" and cloud.resource_type: \"organization\" | score risk_score=100",
            "ruleSql": "SELECT timestamp, protoPayload.authenticationInfo.principalEmail, protoPayload.serviceData.policyDelta\nFROM `logging_project.audit_logs.cloudaudit_googleapis_com_activity`\nWHERE protoPayload.methodName = 'SetIamPolicy'\n  AND resource.type = 'organization'",
            "mitre": ["T1484 - Domain Policy Modification", "T1098 - Account Manipulation"]
        },
        "terraform": """module "org_audit_logs" {
  source = "../../modules/log-export"

  sink_scope       = "organization"
  org_id           = var.org_id
  log_project      = var.log_project
  include_children = true

  log_categories = [
    "admin_activity",
    "system_event",
    "policy_denied"
  ]
}"""
    },

    "02-audit-logs-folder": {
        "id": "02-audit-logs-folder",
        "category": "Core Hub & Infrastructure",
        "num": "02-F",
        "title": "Scenario 02-F · Folder-Scoped Aggregated Audit Sink",
        "subtitle": "Subtree containment · Partitioned trust boundary · Non-org admin deployment",
        "chips": [
            {"text": "FOLDER SUBTREE", "tone": "teal"},
            {"text": "TRUST BOUNDARY", "tone": "cyan"},
            {"text": "< 120MS P99", "tone": "amber"},
            {"text": "LEAST PRIVILEGE", "tone": "pink"}
        ],
        "drawio": "diagrams/02-audit-logs-folder.drawio",
        "imgPng": "../diagrams/02-audit-logs-folder.png",
        "imgSvg": "../diagrams/02-audit-logs-folder.svg",
        "specs": {
            "logNames": "Subtree Cloud Audit Logs: cloudaudit.googleapis.com/*",
            "protocol": "Folder Log Router aggregated sink -> Pub/Sub streaming gRPC",
            "latency": "< 120ms P99 delivery",
            "throughput": "Up to 25,000 eps per folder tree",
            "durability": "Guaranteed delivery across child projects"
        },
        "topology": [
            "Folder contains sensitive business unit projects (e.g. PCI-DSS or HIPAA workloads).",
            "Folder Log Router Aggregated Sink captures all projects within the subtree.",
            "Projects outside the folder remain untouched and unmonitored by this sink.",
            "Streams events into Pub/Sub topic in designated security project."
        ],
        "diagnostics": {
            "trapTitle": "THE #1 TRAP: The Blind Spot (Root Projects Silently Missed)",
            "trapDesc": "Folder sinks ONLY capture events within their specific folder subtree. Sibling folders and root-level projects are completely unmonitored. Use folder sinks only when organizational IAM is legally or organizationally restricted.",
            "trapFix": "gcloud logging sinks describe folder-sink --folder=$FOLDER_ID --format=\"yaml(destination,includeChildren)\"",
            "steps": [
                {
                    "num": 1,
                    "title": "Verify Folder Sink Exists and Includes Children",
                    "cmd": "gcloud logging sinks describe abstract-folder-sink --folder=$FOLDER_ID --format=\"yaml(name,destination,includeChildren,writerIdentity)\""
                },
                {
                    "num": 2,
                    "title": "Verify Folder Sink Writer Identity Has Topic Publisher Rights",
                    "cmd": "WRITER=$(gcloud logging sinks describe abstract-folder-sink --folder=$FOLDER_ID --format=\"value(writerIdentity)\")\ngcloud pubsub topics get-iam-policy abstract-folder-logs --project=$LOG_PROJECT --filter=\"bindings.members:$WRITER\""
                },
                {
                    "num": 3,
                    "title": "Verify Child Projects Inherit Log Router Stream",
                    "cmd": "gcloud logging read 'logName:\"logs/cloudaudit.googleapis.com%2Factivity\"' --folder=$FOLDER_ID --limit=3"
                }
            ]
        },
        "schema": {
            "fields": [
                {"raw": "resource.labels.folder_id", "acs": "cloud.folder.id", "desc": "Parent folder ID of originating project", "util": "Subtree blast radius segmentation"}
            ],
            "ruleTitle": "Actionable SIEM Rule: Project Moved Out of Monitored Security Folder",
            "ruleKql": "vendor: GCP and event.action: \"google.resourcemanager.v3.Projects.MoveProject\" | score risk_score=85",
            "ruleSql": "SELECT timestamp, protoPayload.authenticationInfo.principalEmail, protoPayload.resourceName\nFROM `logging_project.audit_logs.cloudaudit_googleapis_com_activity`\nWHERE protoPayload.methodName = 'google.resourcemanager.v3.Projects.MoveProject'",
            "mitre": ["T1562 - Impair Defenses"]
        },
        "terraform": """module "folder_audit_logs" {
  source = "../../modules/log-export"

  sink_scope       = "folder"
  folder_id        = var.folder_id
  log_project      = var.log_project
  include_children = true
}"""
    },

    "02-audit-logs-project": {
        "id": "02-audit-logs-project",
        "category": "Core Hub & Infrastructure",
        "num": "02-P",
        "title": "Scenario 02-P · Single Project Pilot Pipeline",
        "subtitle": "Rapid PoC validation · Minimal IAM footprint · Zero org-level prerequisites",
        "chips": [
            {"text": "SINGLE PROJECT", "tone": "teal"},
            {"text": "RAPID POC", "tone": "cyan"},
            {"text": "< 100MS P99", "tone": "amber"},
            {"text": "LOCAL BOUNDARY", "tone": "pink"}
        ],
        "drawio": "diagrams/02-audit-logs-project.drawio",
        "imgPng": "../diagrams/02-audit-logs-project.png",
        "imgSvg": "../diagrams/02-audit-logs-project.svg",
        "specs": {
            "logNames": "Project Audit Logs: cloudaudit.googleapis.com/*",
            "protocol": "Project-level Log Router sink -> Pub/Sub streaming gRPC",
            "latency": "< 100ms P99 delivery",
            "throughput": "Up to 5,000 eps for single pilot project",
            "durability": "Immediate pilot data validation"
        },
        "topology": [
            "Single pilot workload project produces audit telemetry.",
            "Local Log Router project sink routes events to Pub/Sub topic.",
            "Abstract Security ingests and demonstrates real-time SIEM value within 10 minutes."
        ],
        "diagnostics": {
            "trapTitle": "THE #1 TRAP: The Toil Spiral (Do Not Deploy Per-Project in Production!)",
            "trapDesc": "Deploying 100 project sinks is operational toil. Each decays independently and hits the 200-sinks-per-container quota. Use project sinks ONLY for pilots, then upgrade to Org Aggregated Sink.",
            "trapFix": "gcloud logging sinks list --project=$PROJECT_ID",
            "steps": [
                {
                    "num": 1,
                    "title": "Verify Local Project Sink Status",
                    "cmd": "gcloud logging sinks describe abstract-pilot-sink --project=$PROJECT_ID"
                }
            ]
        },
        "schema": {
            "fields": [
                {"raw": "protoPayload.methodName", "acs": "event.action", "desc": "Method invoked in pilot project", "util": "PoC event verification"}
            ],
            "ruleTitle": "Actionable SIEM Rule: Pilot Project Admin Role Escalation",
            "ruleKql": "vendor: GCP and event.action: \"SetIamPolicy\" and cloud.project.id: \"$PILOT_PROJECT\" | score risk_score=90",
            "ruleSql": "SELECT timestamp, protoPayload.authenticationInfo.principalEmail\nFROM `pilot_project.audit_logs.cloudaudit_googleapis_com_activity`\nWHERE protoPayload.methodName = 'SetIamPolicy'",
            "mitre": ["T1098 - Account Manipulation"]
        },
        "terraform": """module "pilot_project_sink" {
  source = "../../modules/log-export"

  sink_scope   = "project"
  sink_project = var.pilot_project
  log_project  = var.log_project
}"""
    },

    "03-data-access": {
        "id": "03-data-access",
        "category": "Data Access & Storage Security",
        "num": "03",
        "title": "Scenario 03 · Data Access Audit Telemetry & Object Inspection",
        "subtitle": "BigQuery queries & data mutations · Cloud Storage object reads · Service account impersonation",
        "chips": [
            {"text": "DATA ACCESS AUDIT", "tone": "teal"},
            {"text": "TWO-SWITCH INTERLOCK", "tone": "cyan"},
            {"text": "< 250MS P99", "tone": "amber"},
            {"text": "EXFILTRATION HUNT", "tone": "pink"}
        ],
        "drawio": "diagrams/03-data-access.drawio",
        "imgPng": "../diagrams/03-data-access.png",
        "imgSvg": "../diagrams/03-data-access.svg",
        "specs": {
            "logNames": "cloudaudit.googleapis.com/data_access (DATA_READ, DATA_WRITE, ADMIN_READ)",
            "protocol": "Org IAM AuditConfig + Log Router aggregated sink -> Pub/Sub gRPC",
            "latency": "< 250ms P99 delivery",
            "throughput": "High volume: 10,000 to 50,000+ eps depending on storage & DB activity",
            "durability": "Zero telemetry loss for data exfiltration & compliance audits"
        },
        "topology": [
            "Switch 1 (Generation): Org-level IAM auditConfig enables DATA_READ & DATA_WRITE for BigQuery, Cloud Storage, KMS.",
            "Workload services generate rich data access logs with SQL text, caller identity, and bytes scanned.",
            "Switch 2 (Routing): Log Router Aggregated Sink filter selects 'cloudaudit.googleapis.com/data_access'.",
            "Abstract Security ingests data access logs to detect insider threats and token abuse."
        ],
        "diagnostics": {
            "trapTitle": "THE #1 TRAP: The Two-Switch Interlock (Sink Filter Without IAM AuditConfig)",
            "trapDesc": "Data Access logs are DISABLED by default in GCP to avoid cost runaway! A Log Router sink filter selecting 'data_access' will produce ZERO events unless the Org IAM Policy explicitly enables auditConfigs for that service!",
            "trapFix": "gcloud organizations get-iam-policy $ORG_ID --format=\"yaml(auditConfigs)\"",
            "steps": [
                {
                    "num": 1,
                    "title": "Verify Org IAM AuditConfig Status for BigQuery, Storage, KMS",
                    "cmd": "gcloud organizations get-iam-policy $ORG_ID --format=\"yaml(auditConfigs)\""
                },
                {
                    "num": 2,
                    "title": "Verify Sink Filter Captures Data Access Log Stream",
                    "cmd": "gcloud logging sinks describe abstract-data-access-sink --organization=$ORG_ID --format=\"value(filter)\""
                },
                {
                    "num": 3,
                    "title": "Read Live Data Access Logs Generated in Org",
                    "cmd": "gcloud logging read 'logName:\"logs/cloudaudit.googleapis.com%2Fdata_access\"' --organization=$ORG_ID --limit=3"
                }
            ]
        },
        "schema": {
            "fields": [
                {"raw": "protoPayload.serviceData.jobCompletedEvent.job.jobConfiguration.query.query", "acs": "db.statement", "desc": "Exact SQL text executed in BigQuery query", "util": "SQL injection and mass table extraction discovery"},
                {"raw": "protoPayload.resourceName", "acs": "file.path", "desc": "Exact Cloud Storage bucket and object key path", "util": "Sensitive file download and ransomware tracking"},
                {"raw": "protoPayload.authenticationInfo.serviceAccountKeyName", "acs": "gcp.auth.sa_key_name", "desc": "Static key ID used if authenticating via downloaded key", "util": "Leaked credential and non-WIF usage detection"}
            ],
            "ruleTitle": "Actionable SIEM Rule: Mass BigQuery Data Exfiltration (>1TB Scanned)",
            "ruleKql": "vendor: GCP and event.dataset: \"bigquery.googleapis.com\" and gcp.bigquery.total_billed_bytes > 1099511627776 | score risk_score=90",
            "ruleSql": "SELECT timestamp, protoPayload.authenticationInfo.principalEmail, protoPayload.serviceData.jobCompletedEvent.job.jobStatistics.totalBilledBytes\nFROM `logging_project.audit_logs.cloudaudit_googleapis_com_data_access`\nWHERE protoPayload.serviceName = 'bigquery.googleapis.com'\n  AND CAST(JSON_VALUE(protoPayload.serviceData, '$.jobCompletedEvent.job.jobStatistics.totalBilledBytes') AS INT64) > 1000000000000",
            "mitre": ["T1530 - Data from Cloud Storage Object", "T1567 - Exfiltration Over Web Service"]
        },
        "terraform": """module "data_access_audit" {
  source = "../../modules/log-export"

  sink_scope  = "organization"
  org_id      = var.org_id
  log_project = var.log_project

  log_categories = ["data_access_all"]
  data_access_services = [
    "bigquery.googleapis.com",
    "storage.googleapis.com",
    "cloudkms.googleapis.com",
    "iamcredentials.googleapis.com"
  ]
}"""
    },

    "04-workspace": {
        "id": "04-workspace",
        "category": "Identity & Threat Ingestion",
        "num": "04",
        "title": "Scenario 04 · Google Workspace & Cloud Identity Ingestion",
        "subtitle": "Native Cloud Audit Logs Sharing vs Admin SDK Reports API · Logins, 2SV challenges, OAuth & SAML",
        "chips": [
            {"text": "GOOGLE WORKSPACE", "tone": "teal"},
            {"text": "DUAL PATHWAY", "tone": "cyan"},
            {"text": "< 500MS NATIVE", "tone": "amber"},
            {"text": "TOKEN GOVERNANCE", "tone": "pink"}
        ],
        "drawio": "diagrams/04-workspace.drawio",
        "imgPng": "../diagrams/04-workspace.png",
        "imgSvg": "../diagrams/04-workspace.svg",
        "specs": {
            "logNames": "login.googleapis.com, admin, token, saml, drive, groups",
            "protocol": "Pathway A: Native GCP Audit Sharing (gRPC) · Pathway B: Admin SDK Reports API (HTTPS REST)",
            "latency": "Pathway A: < 500ms real-time · Pathway B: 5-15 min batch poll",
            "throughput": "Scales to 500,000+ active Workspace users",
            "durability": "Complete authentication and directory audit trail"
        },
        "topology": [
            "Workspace users authenticate, grant OAuth tokens, and modify group memberships.",
            "Pathway A (Native): Workspace Admin Console shares audit logs directly to GCP Org Sink (Zero Polling!).",
            "Pathway B (DWD): Service Account with Domain-Wide Delegation polls Admin SDK Reports API for 23 deep app streams.",
            "Events route to Pub/Sub and stream into Abstract Composable SIEM for UEBA threat analysis."
        ],
        "diagnostics": {
            "trapTitle": "THE #1 TRAP: Missing Workspace Audit Sharing or Domain-Wide Delegation Scopes",
            "trapDesc": "Native sharing must be toggled in Admin Console (Account settings -> Legal and compliance -> Sharing options -> GCP). For Pathway B, a Workspace Super Admin must manually authorize the Service Account Client ID in Security -> API Controls!",
            "trapFix": "Verify in Admin Console: admin.google.com -> Security -> Access and data control -> API controls -> Domain-wide delegation",
            "steps": [
                {
                    "num": 1,
                    "title": "Verify Native Workspace Audit Logs Flowing in Org Sink",
                    "cmd": "gcloud logging read 'logName:\"logs/login.googleapis.com%2Flogin\"' --organization=$ORG_ID --limit=3"
                },
                {
                    "num": 2,
                    "title": "Verify Workspace Service Account OAuth Client ID",
                    "cmd": "gcloud iam service-accounts describe abstract-workspace-dwd@$LOG_PROJECT.iam.gserviceaccount.com --format=\"value(oauth2ClientId)\""
                }
            ]
        },
        "schema": {
            "fields": [
                {"raw": "protoPayload.authenticationInfo.principalEmail", "acs": "user.email", "desc": "Workspace human user performing login", "util": "Account takeover & credential stuffing detection"},
                {"raw": "protoPayload.metadata.loginDetails.isSuspicious", "acs": "user.risk.is_suspicious", "desc": "Google ML risk assessment flag", "util": "High-confidence compromised credential alerts"}
            ],
            "ruleTitle": "Actionable SIEM Rule: Suspicious Workspace Login with 2SV Challenge Failure",
            "ruleKql": "vendor: Google and event.dataset: \"google_workspace.audit\" and event.action: \"login_challenge_failed\" | score risk_score=95",
            "ruleSql": "SELECT timestamp, protoPayload.authenticationInfo.principalEmail, protoPayload.requestMetadata.callerIp\nFROM `logging_project.audit_logs.cloudaudit_googleapis_com_data_access`\nWHERE protoPayload.serviceName = 'login.googleapis.com'\n  AND JSON_VALUE(protoPayload.metadata, '$.loginDetails.isSuspicious') = 'true'",
            "mitre": ["T1078.004 - Cloud Accounts", "T1110 - Brute Force"]
        },
        "terraform": """module "workspace_logs" {
  source = "../../modules/workspace"

  sink_scope   = "organization"
  org_id       = var.org_id
  log_project  = var.log_project
  ingest_mode  = "native_audit_sharing"
}"""
    },

    "04-identity-auth-oneuptime": {
        "id": "04-identity-auth-oneuptime",
        "category": "Identity & Threat Ingestion",
        "num": "04-ID",
        "title": "Scenario 04-ID · Identity, Auth & OneUptime Federation Architecture",
        "subtitle": "Service account impersonation · Workload Identity Federation (WIF) · SSO & token lifecycle auditing",
        "chips": [
            {"text": "ONEUPTIME AUDIT", "tone": "teal"},
            {"text": "FIVE AUTH STREAMS", "tone": "cyan"},
            {"text": "< 150MS P99", "tone": "amber"},
            {"text": "SYNTHETIC PROBES", "tone": "pink"}
        ],
        "drawio": "diagrams/04-identity-auth-oneuptime.drawio",
        "imgPng": "../diagrams/04-identity-auth-oneuptime.png",
        "imgSvg": "../diagrams/04-identity-auth-oneuptime.svg",
        "specs": {
            "logNames": "login.googleapis.com, iamcredentials.googleapis.com, sts.googleapis.com, cloudaudit/activity",
            "protocol": "Real-time streaming audit logs + OneUptime synthetic canary probes",
            "latency": "< 150ms P99 delivery",
            "throughput": "Monitors all human, service account, and federated STS token mints",
            "durability": "Zero silent drops with heartbeat synthetic validation"
        },
        "topology": [
            "5 Identity streams: Human Logins, SA Impersonation, Workload Identity (WIF), Static Keys, IAM Changes.",
            "OneUptime canary loop injects synthetic token exchanges to continuously verify pipeline health.",
            "All identity transitions route to Pub/Sub and stream into Abstract ASTRO for real-time privilege escalation alerts."
        ],
        "diagnostics": {
            "trapTitle": "THE #1 TRAP: Service Account Impersonation Invisible Without DATA_READ",
            "trapDesc": "Impersonation methods like GenerateAccessToken and SignBlob emit to DATA_ACCESS logs, NOT Admin Activity! If iamcredentials.googleapis.com is not enabled in Org IAM auditConfig, impersonations are 100% invisible!",
            "trapFix": "gcloud organizations set-iam-policy $ORG_ID updated-audit-policy.yaml",
            "steps": [
                {
                    "num": 1,
                    "title": "Verify IAM Credentials DATA_READ Logging Active",
                    "cmd": "gcloud organizations get-iam-policy $ORG_ID --filter=\"auditConfigs.service:iamcredentials.googleapis.com\""
                },
                {
                    "num": 2,
                    "title": "Read Real-Time Service Account Impersonation Events",
                    "cmd": "gcloud logging read 'protoPayload.serviceName:\"iamcredentials.googleapis.com\"' --organization=$ORG_ID --limit=3"
                }
            ]
        },
        "schema": {
            "fields": [
                {"raw": "protoPayload.requestMetadata.callerIp", "acs": "source.ip", "desc": "IP address requesting token minting", "util": "Token theft and anomalous location hunting"},
                {"raw": "protoPayload.resourceName", "acs": "target.user.name", "desc": "Target Service Account being impersonated", "util": "Privilege escalation path tracing"}
            ],
            "ruleTitle": "Actionable SIEM Rule: Unauthorized Service Account Impersonation",
            "ruleKql": "vendor: GCP and event.action: \"GenerateAccessToken\" and not (user.email in [\"ci-cd@iam.gserviceaccount.com\"]) | score risk_score=95",
            "ruleSql": "SELECT timestamp, protoPayload.authenticationInfo.principalEmail, protoPayload.resourceName\nFROM `logging_project.audit_logs.cloudaudit_googleapis_com_data_access`\nWHERE protoPayload.methodName = 'GenerateAccessToken'",
            "mitre": ["T1078.004 - Cloud Accounts", "T1548 - Abuse Elevation Control Mechanism"]
        },
        "terraform": """module "identity_auth_pipeline" {
  source = "../../modules/log-export"

  sink_scope  = "organization"
  org_id      = var.org_id
  log_project = var.log_project

  log_categories = ["admin_activity", "data_access_all"]
  data_access_services = [
    "iamcredentials.googleapis.com",
    "sts.googleapis.com",
    "login.googleapis.com"
  ]
}"""
    },

    "05-health-alerts": {
        "id": "05-health-alerts",
        "category": "Operations & Governance",
        "num": "05",
        "title": "Scenario 05 · Cloud Monitoring Pipeline Health & Anomaly Alerts",
        "subtitle": "Pub/Sub queue depth · Subscriber lag · Silent drop detection · Dead-letter monitoring",
        "chips": [
            {"text": "SLA MONITORING", "tone": "teal"},
            {"text": "DEAD-MAN SWITCH", "tone": "cyan"},
            {"text": "< 60S EVAL", "tone": "amber"},
            {"text": "INSTANT ESCALATION", "tone": "pink"}
        ],
        "drawio": "diagrams/05-health-alerts.drawio",
        "imgPng": "../diagrams/05-health-alerts.png",
        "imgSvg": "../diagrams/05-health-alerts.svg",
        "specs": {
            "logNames": "Cloud Monitoring Alert Policies: Sink Errors, Subscriber Backlog, Dead-Letter",
            "protocol": "Google Cloud Monitoring -> Pub/Sub Notification Channel & Webhooks",
            "latency": "< 60s metric evaluation window",
            "throughput": "Monitors all platform sinks, topics, and subscriptions 24/7",
            "durability": "Zero silent drops: Proactive alerting before logs breach buffer limits"
        },
        "topology": [
            "Metric 1: Sink export error rate tracks permission revocations in real-time.",
            "Metric 2: Pub/Sub unacknowledged message count detects subscriber stall or network partitioning.",
            "Metric 3: Oldest unacknowledged message age alerts before the 7-day retention limit is breached.",
            "Alert policies trigger automated incidents into Abstract AI-SecOps and OnCall webhooks."
        ],
        "diagnostics": {
            "trapTitle": "THE #1 TRAP: Unacknowledged Message Accumulation Leading to Buffer Purge",
            "trapDesc": "If the Abstract forwarder is offline for 7 days, unacknowledged messages are purged permanently. Alert policy on 'oldest_unacked_message_age' must fire at 24 hours to guarantee zero data loss.",
            "trapFix": "gcloud monitoring alert-policies list --project=$LOG_PROJECT",
            "steps": [
                {
                    "num": 1,
                    "title": "List Configured Alert Policies in Logging Project",
                    "cmd": "gcloud monitoring alert-policies list --project=$LOG_PROJECT --format=\"table(displayName,enabled)\""
                },
                {
                    "num": 2,
                    "title": "Check Pub/Sub Subscription Backlog Size",
                    "cmd": "gcloud pubsub subscriptions describe abstract-audit-logs-sub --project=$LOG_PROJECT --format=\"value(numUndeliveredMessages)\""
                }
            ]
        },
        "schema": {
            "fields": [
                {"raw": "incident.metric.displayName", "acs": "monitoring.metric.name", "desc": "Alert policy metric triggering failure condition", "util": "Pipeline health observability"}
            ],
            "ruleTitle": "Actionable SIEM Rule: Critical Telemetry Pipeline Ingestion Stall",
            "ruleKql": "vendor: GCP and event.dataset: \"cloud_monitoring.alert\" and severity: \"CRITICAL\" | score risk_score=100",
            "ruleSql": "SELECT timestamp, incident.summary\nFROM `logging_project.monitoring.incidents`\nWHERE incident.state = 'OPEN' AND incident.severity = 'CRITICAL'",
            "mitre": ["T1562.001 - Disable or Modify Tools"]
        },
        "terraform": """module "health_monitoring" {
  source = "../../modules/health-alerts"

  project_id        = var.log_project
  subscription_name = "abstract-audit-logs-sub"
  sink_name         = "abstract-org-sink"

  alert_channels = [var.notification_channel_id]
}"""
    },

    "06-scc-findings": {
        "id": "06-scc-findings",
        "category": "Threat Defense & Perimeter",
        "num": "06",
        "title": "Scenario 06 · Security Command Center (SCC) Finding Notifications",
        "subtitle": "Continuous posture assessment · Vulnerabilities & threats · Event Threat Detection (ETD)",
        "chips": [
            {"text": "SCC REAL-TIME PUSH", "tone": "teal"},
            {"text": "EVENT THREAT DETECT", "tone": "cyan"},
            {"text": "< 30S P99", "tone": "amber"},
            {"text": "MITRE ATT&CK MAPPED", "tone": "pink"}
        ],
        "drawio": "diagrams/06-scc-findings.drawio",
        "imgPng": "../diagrams/06-scc-findings.png",
        "imgSvg": "../diagrams/06-scc-findings.svg",
        "specs": {
            "logNames": "Organization NotificationConfig: Event Threat Detection, Container Threat, Web Security",
            "protocol": "SCC Service Agent -> Pub/Sub topic streaming push",
            "latency": "< 30s real-time finding notification delivery",
            "throughput": "Continuous threat streaming across org",
            "durability": "Immediate incident creation in Abstract SIEM"
        },
        "topology": [
            "SCC Event Threat Detection (ETD) analyzes Cloud Logging for crypto mining, malware, brute force.",
            "SCC NotificationConfig routes findings into Pub/Sub topic 'abstract-scc-findings'.",
            "SCC Service Agent (service-org-ID@gcp-sa-scc.iam.gserviceaccount.com) publishes with zero delay.",
            "Abstract Security ingests findings and enriches with ASTRO intelligence."
        ],
        "diagnostics": {
            "trapTitle": "THE #1 TRAP: SCC Service Agent Missing Topic Publisher Rights",
            "trapDesc": "SCC NotificationConfig uses its OWN service agent, NOT the Log Router writer identity! It requires an explicit 'roles/pubsub.publisher' grant on the SCC destination topic.",
            "trapFix": "gcloud pubsub topics add-iam-policy-binding abstract-scc-findings --project=$LOG_PROJECT --member=\"serviceAccount:service-org-$ORG_NUM@gcp-sa-scc.iam.gserviceaccount.com\" --role=\"roles/pubsub.publisher\"",
            "steps": [
                {
                    "num": 1,
                    "title": "Describe SCC Notification Config at Org Scope",
                    "cmd": "gcloud scc notifications describe abstract-scc-feed --organization=$ORG_ID --format=\"yaml(description,pubsubTopic)\""
                }
            ]
        },
        "schema": {
            "fields": [
                {"raw": "finding.category", "acs": "vulnerability.category", "desc": "SCC threat classification category", "util": "Immediate threat grouping & triage"},
                {"raw": "finding.severity", "acs": "event.severity", "desc": "Finding severity: CRITICAL, HIGH, MEDIUM, LOW", "util": "SLA dispatch & escalation"}
            ],
            "ruleTitle": "Actionable SIEM Rule: Critical Container Threat or Crypto Mining Finding",
            "ruleKql": "vendor: GCP and event.dataset: \"gcp.scc_findings\" and event.severity in [\"CRITICAL\", \"HIGH\"] | score risk_score=100",
            "ruleSql": "SELECT timestamp, raw.finding.name, raw.finding.category, raw.finding.severity\nFROM `logging_project.scc.findings`\nWHERE raw.finding.state = 'ACTIVE'\n  AND raw.finding.severity IN ('CRITICAL', 'HIGH')",
            "mitre": ["T1496 - Resource Hijacking", "T1610 - Deploy Container"]
        },
        "terraform": """resource "google_scc_organization_notification_config" "abstract_feed" {
  config_id    = "abstract-scc-feed"
  organization = var.org_id
  pubsub_topic = module.logging_project.topic_id

  streaming_config {
    filter = "state=\\"ACTIVE\\""
  }
}"""
    },

    "07-asset-inventory": {
        "id": "07-asset-inventory",
        "category": "Threat Defense & Perimeter",
        "num": "07",
        "title": "Scenario 07 · Cloud Asset Inventory Real-Time Resource & IAM Feeds",
        "subtitle": "Continuous infrastructure mutation tracking · Resource diffs · Temporal IAM changes",
        "chips": [
            {"text": "ASSET MUTATION FEED", "tone": "teal"},
            {"text": "RESOURCE DIFFS", "tone": "cyan"},
            {"text": "< 60S P99", "tone": "amber"},
            {"text": "STATE RECONCILIATION", "tone": "pink"}
        ],
        "drawio": "diagrams/07-asset-inventory.drawio",
        "imgPng": "../diagrams/07-asset-inventory.png",
        "imgSvg": "../diagrams/07-asset-inventory.svg",
        "specs": {
            "logNames": "Cloud Asset Inventory Feed: RESOURCE mutations and IAM_POLICY state transitions",
            "protocol": "CAI Service Agent -> Pub/Sub streaming push",
            "latency": "< 60s real-time asset change delivery",
            "throughput": "Captures all resource creation, deletion, and policy diffs",
            "durability": "Deterministic asset ledger in Abstract LakeVilla"
        },
        "topology": [
            "Compute, Storage, Network, and IAM resources mutate across the Organization.",
            "Cloud Asset Inventory Organization Feed captures real-time state deltas.",
            "Feeds push changes into Pub/Sub topic 'abstract-asset-inventory'.",
            "Abstract Security constructs a temporal infrastructure timeline for breach forensics."
        ],
        "diagnostics": {
            "trapTitle": "THE #1 TRAP: CAI Service Agent Missing Pub/Sub Publisher Role",
            "trapDesc": "The Cloud Asset Inventory service agent (service-PROJECT_NUM@gcp-sa-cai.iam.gserviceaccount.com) must be granted roles/pubsub.publisher on the topic before creating the feed, or feed creation fails immediately.",
            "trapFix": "gcloud pubsub topics add-iam-policy-binding abstract-asset-inventory --project=$LOG_PROJECT --member=\"serviceAccount:service-$LOG_PROJECT_NUM@gcp-sa-cai.iam.gserviceaccount.com\" --role=\"roles/pubsub.publisher\"",
            "steps": [
                {
                    "num": 1,
                    "title": "List Active Cloud Asset Inventory Feeds at Org Scope",
                    "cmd": "gcloud asset feeds list --organization=$ORG_ID --format=\"table(name,contentType,feedOutputConfig.pubsubDestination.topic)\""
                }
            ]
        },
        "schema": {
            "fields": [
                {"raw": "asset.assetType", "acs": "cloud.resource.type", "desc": "Resource classification type (e.g. compute.googleapis.com/Firewall)", "util": "Attack surface exposure tracking"},
                {"raw": "asset.resource.data", "acs": "cloud.resource.configuration", "desc": "Complete JSON configuration snapshot of asset", "util": "Configuration drift detection"}
            ],
            "ruleTitle": "Actionable SIEM Rule: Public Cloud Storage Bucket Created or Modified",
            "ruleKql": "vendor: GCP and event.dataset: \"gcp.asset_inventory\" and gcp.asset.type: \"storage.googleapis.com/Bucket\" and gcp.asset.iam.is_public: true | score risk_score=95",
            "ruleSql": "SELECT timestamp, asset.name, asset.iamPolicy\nFROM `logging_project.asset_inventory.feeds`\nWHERE asset.assetType = 'storage.googleapis.com/Bucket'\n  AND EXISTS(SELECT 1 FROM UNNEST(asset.iamPolicy.bindings) WHERE 'allUsers' IN UNNEST(members))",
            "mitre": ["T1530 - Data from Cloud Storage Object"]
        },
        "terraform": """resource "google_cloud_asset_organization_feed" "abstract_feed" {
  feed_id         = "abstract-asset-feed"
  org_id          = var.org_id
  content_type    = "RESOURCE"
  asset_types     = ["*"]

  feed_output_config {
    pubsub_destination {
      topic = module.logging_project.topic_id
    }
  }
}"""
    },

    "08-bucket-logs": {
        "id": "08-bucket-logs",
        "category": "Data Access & Storage Security",
        "num": "08",
        "title": "Scenario 08 · Cloud Storage Bucket Telemetry & Notifications",
        "subtitle": "Object uploads, downloads, deletions & lifecycle events · Real-time exfiltration detection",
        "chips": [
            {"text": "BUCKET NOTIFICATIONS", "tone": "teal"},
            {"text": "OBJECT EVENTS", "tone": "cyan"},
            {"text": "< 150MS P99", "tone": "amber"},
            {"text": "STORAGE PERIMETER", "tone": "pink"}
        ],
        "drawio": "diagrams/08-bucket-logs.drawio",
        "imgPng": "../diagrams/08-bucket-logs.png",
        "imgSvg": "../diagrams/08-bucket-logs.svg",
        "specs": {
            "logNames": "Cloud Storage Pub/Sub Object Change Notifications: OBJECT_FINALIZE, OBJECT_DELETE, OBJECT_ARCHIVE",
            "protocol": "GCS Service Agent -> Pub/Sub streaming notification push",
            "latency": "< 150ms P99 object mutation event delivery",
            "throughput": "Scales to millions of object transitions per hour",
            "durability": "Deterministic storage audit trail"
        },
        "topology": [
            "Workload buckets in customer projects receive uploads, downloads, and lifecycle deletions.",
            "GCS Bucket Notification config registers Pub/Sub topic in central logging project.",
            "GCS Service Agent publishes JSON notifications with object size, MD5, and metadata.",
            "Abstract Security analyzes object churn rates to detect ransomware or bulk exfiltration."
        ],
        "diagnostics": {
            "trapTitle": "THE #1 TRAP: Storage Service Agent Missing Topic Publisher Permission",
            "trapDesc": "The Cloud Storage service account for the bucket's project (service-PROJECT_NUM@gs-project-accounts.iam.gserviceaccount.com) must have roles/pubsub.publisher on the destination topic!",
            "trapFix": "gsutil notification create -t abstract-bucket-logs -f json gs://$BUCKET_NAME",
            "steps": [
                {
                    "num": 1,
                    "title": "List Notifications Configured on Storage Bucket",
                    "cmd": "gcloud storage buckets notifications list --bucket=gs://$BUCKET_NAME"
                }
            ]
        },
        "schema": {
            "fields": [
                {"raw": "name", "acs": "file.name", "desc": "Object key name uploaded or modified in bucket", "util": "Ransomware extension and credential file hunting"}
            ],
            "ruleTitle": "Actionable SIEM Rule: Bulk Cloud Storage Object Deletions (Ransomware)",
            "ruleKql": "vendor: GCP and event.action: \"OBJECT_DELETE\" | count() by user.email > 500 in 5m | score risk_score=95",
            "ruleSql": "SELECT timestamp, name, bucket\nFROM `logging_project.bucket_events.notifications`\nWHERE eventType = 'OBJECT_DELETE'",
            "mitre": ["T1485 - Data Destruction"]
        },
        "terraform": """resource "google_storage_notification" "bucket_notification" {
  bucket         = var.monitored_bucket_name
  payload_format = "JSON_API_V1"
  topic          = module.logging_project.topic_id
  event_types    = ["OBJECT_FINALIZE", "OBJECT_DELETE", "OBJECT_ARCHIVE"]
}"""
    },

    "09-log-archive": {
        "id": "09-log-archive",
        "category": "Data Access & Storage Security",
        "num": "09",
        "title": "Scenario 09 · Dual-Routing & Long-Term GCS Coldline Archive",
        "subtitle": "Non-disruptive migration · Simultaneous Abstract SIEM ingestion + immutable Coldline compliance retention",
        "chips": [
            {"text": "DUAL ROUTING", "tone": "teal"},
            {"text": "WORM RETENTION", "tone": "cyan"},
            {"text": "PARALLEL SINKS", "tone": "amber"},
            {"text": "ZERO DISRUPTION", "tone": "pink"}
        ],
        "drawio": "diagrams/09-log-archive.drawio",
        "imgPng": "../diagrams/09-log-archive.png",
        "imgSvg": "../diagrams/09-log-archive.svg",
        "specs": {
            "logNames": "Parallel Log Router Sinks: Sink 1 (Pub/Sub) + Sink 2 (GCS Coldline)",
            "protocol": "Simultaneous streaming gRPC + immutable GCS batch writing",
            "latency": "Stream: < 100ms P99 · Archive: hourly batch finalized",
            "throughput": "Dual-routed with zero backpressure on real-time stream",
            "durability": "Immutable WORM compliance retention (365+ days)"
        },
        "topology": [
            "Log Router receives organization audit events.",
            "Sink 1 routes to Pub/Sub topic 'abstract-audit-logs' for real-time SIEM analytics.",
            "Sink 2 runs in parallel, routing identical events directly into GCS bucket 'abstract-gcp-archive'.",
            "GCS Bucket Lock enforces immutable retention for SEC 17a-4 and PCI compliance."
        ],
        "diagnostics": {
            "trapTitle": "THE #1 TRAP: Parallel GCS Sink Writer Identity Missing Bucket Storage Admin",
            "trapDesc": "Sink 2 has its OWN unique writerIdentity. It must be granted roles/storage.objectCreator on the archive bucket, otherwise compliance archiving fails while SIEM ingestion continues!",
            "trapFix": "WRITER=$(gcloud logging sinks describe gcs-archive-sink --organization=$ORG_ID --format=\"value(writerIdentity)\")\ngcloud storage buckets add-iam-policy-binding gs://abstract-gcp-archive --member=\"$WRITER\" --role=\"roles/storage.objectCreator\"",
            "steps": [
                {
                    "num": 1,
                    "title": "Verify Dual Sinks Both Active at Org Scope",
                    "cmd": "gcloud logging sinks list --organization=$ORG_ID --format=\"table(name,destination)\""
                }
            ]
        },
        "schema": {
            "fields": [
                {"raw": "archive.bucket", "acs": "storage.bucket.name", "desc": "Coldline compliance bucket holding encrypted raw archives", "util": "Legal hold and forensic reconstruction"}
            ],
            "ruleTitle": "Actionable SIEM Rule: Unauthorized GCS Log Archive Lifecycle or Policy Mutation",
            "ruleKql": "vendor: GCP and cloud.resource_type: \"storage.googleapis.com/Bucket\" and event.action: \"storage.setIamPermissions\" | score risk_score=100",
            "ruleSql": "SELECT timestamp, protoPayload.authenticationInfo.principalEmail\nFROM `logging_project.audit_logs.cloudaudit_googleapis_com_activity`\nWHERE protoPayload.resourceName LIKE '%abstract-gcp-archive%'\n  AND protoPayload.methodName = 'storage.setIamPermissions'",
            "mitre": ["T1562.001 - Disable or Modify Tools"]
        },
        "terraform": """module "archive_dual_pipeline" {
  source = "../../modules/log-export"

  sink_scope   = "organization"
  org_id       = var.org_id
  log_project  = var.log_project

  enable_archive_sink = true
  archive_bucket_name = "acme-abstract-gcp-archive"
  archive_retention_days = 365
}"""
    },

    "10-billing-account": {
        "id": "10-billing-account",
        "category": "Operations & Governance",
        "num": "10",
        "title": "Scenario 10 · Billing Account Audit Logs (Outside Hierarchy)",
        "subtitle": "Billing IAM mutations · Cost anomalies · Billing account sinks · Non-hierarchical trust boundary",
        "chips": [
            {"text": "OUTSIDE HIERARCHY", "tone": "teal"},
            {"text": "FINANCIAL CONTROL", "tone": "cyan"},
            {"text": "< 200MS P99", "tone": "amber"},
            {"text": "FRAUD DETECTION", "tone": "pink"}
        ],
        "drawio": "diagrams/10-billing-account.drawio",
        "imgPng": "../diagrams/10-billing-account.png",
        "imgSvg": "../diagrams/10-billing-account.svg",
        "specs": {
            "logNames": "billingaccounts.googleapis.com/*, budget, credit, project link/unlink",
            "protocol": "Billing Account Log Router Sink -> Pub/Sub streaming gRPC",
            "latency": "< 200ms P99 delivery",
            "throughput": "Dedicated financial audit stream",
            "durability": "Tamper-evident financial change log"
        },
        "topology": [
            "Billing accounts sit OUTSIDE the Organization resource tree entirely.",
            "Org-level and Folder-level sinks NEVER capture billing account events!",
            "Dedicated billing-scoped sink (google_logging_billing_account_sink) is required.",
            "Routes financial events into Pub/Sub topic in logging project for fraud alerting."
        ],
        "diagnostics": {
            "trapTitle": "THE #1 TRAP: The Hierarchy Myth (Org Sinks Do NOT Capture Billing Logs!)",
            "trapDesc": "Assuming an Org Aggregated Sink captures billing events is the #1 cloud security audit failure. Billing accounts exist in a separate control plane! You must create a dedicated billing_account sink using roles/logging.configWriter granted directly ON the billing account.",
            "trapFix": "gcloud logging sinks create abstract-billing-sink pubsub.googleapis.com/projects/$LOG_PROJECT/topics/abstract-billing-logs --billing-account=$BILLING_ACCOUNT_ID",
            "steps": [
                {
                    "num": 1,
                    "title": "Verify IAM Role on Billing Account",
                    "cmd": "gcloud billing accounts get-iam-policy $BILLING_ACCOUNT_ID --flatten=\"bindings[].members\" --filter=\"bindings.role:roles/logging.configWriter\""
                },
                {
                    "num": 2,
                    "title": "Verify Billing Sink Configured Directly on Billing Account",
                    "cmd": "gcloud logging sinks describe abstract-billing-sink --billing-account=$BILLING_ACCOUNT_ID --format=\"yaml(destination,writerIdentity)\""
                }
            ]
        },
        "schema": {
            "fields": [
                {"raw": "protoPayload.methodName", "acs": "event.action", "desc": "Billing RPC action (e.g. LinkProject, CloseBillingAccount)", "util": "Financial fraud and denial of service detection"}
            ],
            "ruleTitle": "Actionable SIEM Rule: Project Linked to Billing Account Outside Whitelist",
            "ruleKql": "vendor: GCP and event.action: \"google.cloud.billing.v1.CloudBilling.UpdateProjectBillingInfo\" | score risk_score=90",
            "ruleSql": "SELECT timestamp, protoPayload.authenticationInfo.principalEmail, protoPayload.resourceName\nFROM `logging_project.billing_audit.cloudaudit_googleapis_com_activity`\nWHERE protoPayload.methodName = 'google.cloud.billing.v1.CloudBilling.UpdateProjectBillingInfo'",
            "mitre": ["T1496 - Resource Hijacking"]
        },
        "terraform": """module "billing_audit" {
  source = "../../modules/log-export"

  sink_scope         = "billing_account"
  billing_account_id = var.billing_account_id
  log_project        = var.log_project
  topic_name         = "abstract-billing-audit-logs"
}"""
    },

    "11-network-threats": {
        "id": "11-network-threats",
        "category": "Threat Defense & Perimeter",
        "num": "11",
        "title": "Scenario 11 · Network Threat Defense & Edge Perimeter Ingestion",
        "subtitle": "Cloud Armor WAF · Cloud IDS threat logs · VPC Flow Logs · Cloud DNS query telemetry",
        "chips": [
            {"text": "HIGH-VOLUME TELEMETRY", "tone": "teal"},
            {"text": "DEDICATED TOPIC", "tone": "cyan"},
            {"text": "50,000+ EPS", "tone": "amber"},
            {"text": "EDGE WAF DEFENSE", "tone": "pink"}
        ],
        "drawio": "diagrams/11-network-threats.drawio",
        "imgPng": "../diagrams/11-network-threats.png",
        "imgSvg": "../diagrams/11-network-threats.svg",
        "specs": {
            "logNames": "Cloud Armor WAF decisions, Cloud IDS threats, Cloud DNS queries, Firewall logs",
            "protocol": "Dedicated High-Throughput Aggregated Sink -> Dedicated 50k+ EPS Pub/Sub Topic",
            "latency": "< 120ms P99 delivery",
            "throughput": "Engineered for 50,000 to 100,000+ eps peak traffic bursts",
            "durability": "Noisy neighbor isolation: Never starves admin audit pipeline"
        },
        "topology": [
            "Edge & network perimeters produce 100x to 1,000x the volume of administrative logs.",
            "Dedicated high-volume Log Router sink routes exclusively to 'abstract-network-threats'.",
            "Cloud Armor WAF block/allow decisions and Cloud IDS SNORT signatures stream without throttling.",
            "Abstract Security normalizes network flows to detect C2 beacons, SQLi, and port scans."
        ],
        "diagnostics": {
            "trapTitle": "THE #1 TRAP: Mixing Network Telemetry with Administrative Audit Logs",
            "trapDesc": "Routing DNS queries or VPC Flow Logs into the same topic as IAM audit logs causes catastrophic quota exhaustion during a DDoS attack. Administrative audit logs are dropped when you need them most! Network logs MUST use a dedicated topic.",
            "trapFix": "Deploy deployments/11-network-threats to maintain dedicated, isolated transport.",
            "steps": [
                {
                    "num": 1,
                    "title": "Verify Cloud Armor Logging Enabled on Backend Services",
                    "cmd": "gcloud compute backend-services list --format=\"table(name,securityPolicy,logConfig.enable)\""
                },
                {
                    "num": 2,
                    "title": "Verify VPC DNS Query Logging Active on VPC Networks",
                    "cmd": "gcloud dns policies list --format=\"table(name,enableLogging,networks[].targetNetwork)\""
                }
            ]
        },
        "schema": {
            "fields": [
                {"raw": "jsonPayload.enforcedSecurityPolicy.action", "acs": "rule.action", "desc": "Cloud Armor decision: ALLOW, DENY, RATE_BASED_BAN", "util": "Layer 7 attack discovery"},
                {"raw": "jsonPayload.threat_id", "acs": "threat.indicator.id", "desc": "Cloud IDS detected threat signature identifier", "util": "Palo Alto Networks threat intel matching"}
            ],
            "ruleTitle": "Actionable SIEM Rule: Cloud Armor SQLi Block Followed by Cloud IDS Alert",
            "ruleKql": "vendor: GCP and event.dataset: \"gcp.network_threats\" and rule.action: \"DENY\" | count() by source.ip > 10 in 1m | score risk_score=95",
            "ruleSql": "SELECT timestamp, jsonPayload.client_ip, jsonPayload.threat_id\nFROM `logging_project.network_logs.ids_googleapis_com_threat`\nWHERE jsonPayload.alert_severity = 'HIGH'",
            "mitre": ["T1190 - Exploit Public-Facing Application", "T1071 - Application Layer Protocol"]
        },
        "terraform": """module "network_threats_pipeline" {
  source = "../../modules/log-export"

  sink_scope  = "organization"
  org_id      = var.org_id
  log_project = var.log_project

  topic_name        = "abstract-network-threats"
  subscription_name = "abstract-network-threats-sub"

  log_categories = [
    "firewall",
    "dns_queries",
    "load_balancer"
  ]
  platform_log_filters = [
    "ids.googleapis.com%2Fthreat"
  ]
  acknowledge_high_volume = true
}"""
    },

    "01-sink-scope": {
        "id": "01-sink-scope",
        "category": "Operations & Governance",
        "num": "SCOPE",
        "title": "Architecture Reference · Comparative Sink Scope Matrix",
        "subtitle": "Organization vs Folder vs Project vs Billing sinks · Blast radius · Hierarchy containment",
        "chips": [
            {"text": "ARCH REFERENCE", "tone": "teal"},
            {"text": "HIERARCHY MODEL", "tone": "cyan"},
            {"text": "BLAST RADIUS", "tone": "amber"},
            {"text": "DECISION GUIDE", "tone": "pink"}
        ],
        "drawio": "diagrams/01-sink-scope.drawio",
        "imgPng": "../diagrams/01-sink-scope.png",
        "imgSvg": "../diagrams/01-sink-scope.svg",
        "specs": {
            "logNames": "Comparative Architectural Boundary Matrix across GCP Hierarchy",
            "protocol": "Log Router aggregated sinks & Billing sinks",
            "latency": "Universal architecture sizing reference",
            "throughput": "Evaluates org vs folder vs project throughput",
            "durability": "Determines optimal deployment footprint"
        },
        "topology": [
            "Ring 1 (Organization): Covers all folders, projects, and future resources forever.",
            "Ring 2 (Folder): Restricts telemetry to a partitioned folder subtree; misses root projects.",
            "Ring 3 (Project): Covers single project only; linear toil if repeated.",
            "Ring 4 (Billing Account): Completely outside resource hierarchy; requires dedicated sink."
        ],
        "diagnostics": {
            "trapTitle": "THE #1 TRAP: Picking Project Sinks Instead of Org Sink",
            "trapDesc": "Creating project sinks leads to unmanageable IAM sprawl and hit quotas. Always deploy Organization scope unless restricted by strict legal compliance boundaries.",
            "trapFix": "Use deployments/02-audit-logs-organization for permanent full-estate coverage.",
            "steps": [
                {
                    "num": 1,
                    "title": "Check User Permissions at Organization Scope",
                    "cmd": "gcloud organizations get-iam-policy $ORG_ID --flatten=\"bindings[].members\" --filter=\"bindings.role:roles/logging.configWriter\""
                }
            ]
        },
        "schema": {
            "fields": [
                {"raw": "resource.type", "acs": "cloud.resource.type", "desc": "Resource type boundary (organization, folder, project, billing_account)", "util": "Scope identification"}
            ],
            "ruleTitle": "Actionable SIEM Rule: Log Sink Deleted or Filter Tampered at Any Scope",
            "ruleKql": "vendor: GCP and event.action in [\"google.logging.v2.ConfigServiceV2.DeleteSink\", \"google.logging.v2.ConfigServiceV2.UpdateSink\"] | score risk_score=100",
            "ruleSql": "SELECT timestamp, protoPayload.authenticationInfo.principalEmail, protoPayload.resourceName\nFROM `logging_project.audit_logs.cloudaudit_googleapis_com_activity`\nWHERE protoPayload.methodName LIKE '%ConfigServiceV2%Sink%'",
            "mitre": ["T1562.001 - Disable or Modify Tools"]
        },
        "terraform": """# Choose scope based on authority:
# 1. Organization: deployments/02-audit-logs-organization
# 2. Folder:       deployments/02-audit-logs-folder
# 3. Project:      deployments/02-audit-logs-project
# 4. Billing:      deployments/10-billing-account"""
    },

    "03-log-router-boundary": {
        "id": "03-log-router-boundary",
        "category": "Operations & Governance",
        "num": "BOUND",
        "title": "Architecture Reference · Log Router Ingestion Boundaries",
        "subtitle": "What sink filters can collect vs what requires independent notification configs",
        "chips": [
            {"text": "BOUNDARY REFERENCE", "tone": "teal"},
            {"text": "SINK CAPABILITY", "tone": "cyan"},
            {"text": "COST OPTIMIZED", "tone": "amber"},
            {"text": "ZERO EGRESS WASTE", "tone": "pink"}
        ],
        "drawio": "diagrams/03-log-router-boundary.drawio",
        "imgPng": "../diagrams/03-log-router-boundary.png",
        "imgSvg": "../diagrams/03-log-router-boundary.svg",
        "specs": {
            "logNames": "Log Router inclusion capabilities vs independent notification APIs",
            "protocol": "Unified Log Router vs SCC Notifications vs CAI Feeds vs GCS Notifications",
            "latency": "Clarifies routing mechanisms for enterprise security architecture",
            "throughput": "Prevents redundant or missing pipeline deployments",
            "durability": "Complete data-source map for GCP"
        },
        "topology": [
            "Log Router Sinks collect: Audit Logs, Network Logs, GKE control plane, Cloud SQL, System events.",
            "Independent Feeds collect: SCC Findings (NotificationConfig), Asset Feeds (CAI), Storage Object Notifications (gsutil notification).",
            "Combining Log Router with SCC and CAI provides complete 360-degree security visibility."
        ],
        "diagnostics": {
            "trapTitle": "THE #1 TRAP: Trying to Route SCC Findings or Asset Feeds via Log Router",
            "trapDesc": "SCC Findings and Cloud Asset Inventory feeds do NOT pass through Cloud Logging! Attempting to write a Log Router filter for them produces zero logs. They require independent Pub/Sub notification configs.",
            "trapFix": "Deploy deployments/06-scc-findings and deployments/07-asset-inventory.",
            "steps": [
                {
                    "num": 1,
                    "title": "Verify SCC Notification Configs Independent of Logging",
                    "cmd": "gcloud scc notifications list --organization=$ORG_ID"
                }
            ]
        },
        "schema": {
            "fields": [
                {"raw": "logName", "acs": "event.dataset", "desc": "Log Router canonical log stream identifier", "util": "Telemetry ingestion routing"}
            ],
            "ruleTitle": "Actionable SIEM Rule: Log Router Ingestion Boundary Exclusion Rule Added",
            "ruleKql": "vendor: GCP and event.action: \"google.logging.v2.ConfigServiceV2.CreateExclusion\" | score risk_score=85",
            "ruleSql": "SELECT timestamp, protoPayload.authenticationInfo.principalEmail, protoPayload.request\nFROM `logging_project.audit_logs.cloudaudit_googleapis_com_activity`\nWHERE protoPayload.methodName = 'google.logging.v2.ConfigServiceV2.CreateExclusion'",
            "mitre": ["T1562.001 - Disable or Modify Tools"]
        },
        "terraform": """# Log Router Boundary Architecture
# Deploy deployments/02-audit-logs-organization for all Log Router telemetry
# Deploy deployments/06-scc-findings for SCC threat notifications
# Deploy deployments/07-asset-inventory for CAI asset mutation feeds"""
    }
}

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Abstract Security · GCP Architecture &amp; Diagnostics Explorer</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Barlow+Semi+Condensed:wght@400;600;700&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg: #060608;
      --panel: #0d1117;
      --panel-elevated: #161b22;
      --panel-border: #21262d;
      --pink: #FF216B;
      --pink-glow: rgba(255, 33, 107, 0.4);
      --teal: #01E69D;
      --teal-glow: rgba(1, 230, 157, 0.35);
      --blue: #2E9BF0;
      --cyan: #00D2FF;
      --amber: #F5C61E;
      --ink: #ECEFF1;
      --muted: #8B949E;
      --code-bg: #090d13;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      background-color: var(--bg);
      color: var(--ink);
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
      display: flex;
      height: 100vh;
      overflow: hidden;
    }

    /* Sidebar Navigation */
    .sidebar {
      width: 340px;
      background: var(--panel);
      border-right: 1px solid var(--panel-border);
      display: flex;
      flex-direction: column;
      flex-shrink: 0;
      height: 100%;
    }

    .brand-header {
      padding: 20px;
      border-bottom: 1px solid var(--panel-border);
      display: flex;
      align-items: center;
      gap: 12px;
      background: rgba(255, 33, 107, 0.03);
    }

    .brand-logo-wrap {
      width: 36px;
      height: 36px;
      display: flex;
      align-items: center;
      justify-content: center;
      filter: drop-shadow(0 0 10px var(--pink-glow));
    }
    .brand-logo-wrap svg { width: 36px; height: 36px; }

    .brand-title {
      font-family: 'Barlow Semi Condensed', sans-serif;
      font-size: 19px;
      font-weight: 700;
      color: var(--pink);
      letter-spacing: 0.5px;
      line-height: 1.1;
    }

    .brand-sub {
      font-size: 11px;
      color: var(--muted);
      letter-spacing: 0.3px;
      margin-top: 2px;
    }

    .search-box {
      padding: 12px 16px;
      border-bottom: 1px solid var(--panel-border);
    }
    .search-input {
      width: 100%;
      background: var(--bg);
      border: 1px solid var(--panel-border);
      border-radius: 6px;
      padding: 8px 12px;
      color: var(--ink);
      font-size: 12px;
      font-family: 'Inter', sans-serif;
      outline: none;
      transition: border-color 0.15s ease;
    }
    .search-input:focus {
      border-color: var(--pink);
      box-shadow: 0 0 8px var(--pink-glow);
    }

    .scenario-list {
      flex: 1;
      overflow-y: auto;
      padding: 12px;
    }

    .category-title {
      font-size: 10px;
      text-transform: uppercase;
      letter-spacing: 1px;
      color: var(--muted);
      margin: 16px 8px 6px;
      font-weight: 700;
      font-family: 'Barlow Semi Condensed', sans-serif;
    }

    .scenario-item {
      padding: 10px 12px;
      border-radius: 6px;
      margin-bottom: 4px;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: space-between;
      transition: all 0.15s ease;
      border: 1px solid transparent;
      font-size: 12px;
    }
    .scenario-item:hover {
      background: rgba(255, 255, 255, 0.04);
      border-color: rgba(255, 255, 255, 0.08);
    }
    .scenario-item.active {
      background: rgba(255, 33, 107, 0.1);
      border-color: var(--pink);
      color: #fff;
      box-shadow: 0 0 14px rgba(255, 33, 107, 0.2);
    }

    .scenario-name {
      display: flex;
      align-items: center;
      gap: 8px;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    .scenario-tag {
      font-family: 'JetBrains Mono', monospace;
      font-size: 10px;
      padding: 2px 6px;
      border-radius: 4px;
      background: rgba(255, 255, 255, 0.06);
      color: var(--muted);
      flex-shrink: 0;
    }
    .scenario-item.active .scenario-tag {
      background: var(--pink);
      color: #fff;
      font-weight: 600;
    }

    /* Main Content Area */
    .main {
      flex: 1;
      display: flex;
      flex-direction: column;
      overflow: hidden;
      background: var(--bg);
    }

    .topbar {
      padding: 16px 28px;
      background: var(--panel);
      border-bottom: 1px solid var(--panel-border);
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-shrink: 0;
    }

    .scenario-header h1 {
      font-family: 'Barlow Semi Condensed', sans-serif;
      font-size: 22px;
      font-weight: 700;
      color: var(--pink);
      display: flex;
      align-items: center;
      gap: 10px;
    }
    .scenario-header p {
      font-size: 12px;
      color: var(--muted);
      margin-top: 4px;
    }

    .hud-bar {
      display: flex;
      gap: 8px;
    }
    .hud-chip {
      padding: 4px 10px;
      border-radius: 20px;
      font-family: 'JetBrains Mono', monospace;
      font-size: 10px;
      font-weight: 600;
      background: var(--bg);
      border: 1px solid;
      display: flex;
      align-items: center;
      gap: 6px;
    }
    .hud-chip.teal { border-color: var(--teal); color: var(--teal); box-shadow: 0 0 8px var(--teal-glow); }
    .hud-chip.cyan { border-color: var(--cyan); color: var(--cyan); }
    .hud-chip.amber { border-color: var(--amber); color: var(--amber); }
    .hud-chip.pink { border-color: var(--pink); color: var(--pink); }

    .actions-bar {
      display: flex;
      gap: 8px;
      align-items: center;
    }
    .btn {
      padding: 6px 14px;
      border-radius: 6px;
      font-size: 12px;
      font-weight: 600;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      text-decoration: none;
      transition: all 0.15s ease;
      font-family: 'Inter', sans-serif;
    }
    .btn-primary {
      background: var(--pink);
      color: #fff;
      border: 1px solid var(--pink);
      box-shadow: 0 0 12px var(--pink-glow);
    }
    .btn-primary:hover { background: #e0175b; }
    .btn-secondary {
      background: rgba(255, 255, 255, 0.05);
      color: var(--ink);
      border: 1px solid var(--panel-border);
    }
    .btn-secondary:hover { background: rgba(255, 255, 255, 0.1); border-color: var(--muted); }

    /* Nav Tabs */
    .nav-tabs {
      display: flex;
      padding: 0 28px;
      background: var(--panel);
      border-bottom: 1px solid var(--panel-border);
      gap: 28px;
      flex-shrink: 0;
    }
    .tab-btn {
      padding: 12px 0;
      background: none;
      border: none;
      color: var(--muted);
      font-size: 13px;
      font-weight: 600;
      cursor: pointer;
      position: relative;
      transition: color 0.15s ease;
      font-family: 'Barlow Semi Condensed', sans-serif;
      letter-spacing: 0.3px;
    }
    .tab-btn:hover { color: var(--ink); }
    .tab-btn.active { color: var(--pink); }
    .tab-btn.active::after {
      content: '';
      position: absolute;
      bottom: -1px;
      left: 0;
      right: 0;
      height: 2px;
      background: var(--pink);
      box-shadow: 0 0 8px var(--pink-glow);
    }

    /* Content Area */
    .content-area {
      flex: 1;
      overflow-y: auto;
      padding: 24px 28px;
      position: relative;
    }
    .tab-pane { display: none; height: 100%; }
    .tab-pane.active { display: block; }

    /* Viewer Container */
    .viewer-frame {
      background: var(--panel);
      border: 1px solid var(--panel-border);
      border-radius: 8px;
      overflow: hidden;
      display: flex;
      flex-direction: column;
      height: 100%;
      min-height: 720px;
      position: relative;
    }

    .viewer-toolbar {
      padding: 8px 16px;
      background: var(--panel-elevated);
      border-bottom: 1px solid var(--panel-border);
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 11px;
    }
    .viewer-controls {
      display: flex;
      gap: 6px;
    }
    .tool-btn {
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid var(--panel-border);
      color: var(--ink);
      padding: 4px 8px;
      border-radius: 4px;
      cursor: pointer;
      font-size: 11px;
    }
    .tool-btn:hover { background: rgba(255, 255, 255, 0.1); }

    .viewer-img-container {
      flex: 1;
      display: flex;
      align-items: center;
      justify-content: center;
      background: #04060c;
      overflow: auto;
      padding: 24px;
      position: relative;
    }
    .viewer-img {
      max-width: 100%;
      max-height: 100%;
      border-radius: 4px;
      box-shadow: 0 8px 32px rgba(0, 0, 0, 0.85);
      transition: transform 0.2s ease;
    }

    /* Info Cards & Tables */
    .info-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 16px;
      margin-bottom: 24px;
    }
    .info-card {
      background: var(--panel);
      border: 1px solid var(--panel-border);
      border-radius: 8px;
      padding: 16px;
    }
    .info-card h4 {
      font-size: 11px;
      text-transform: uppercase;
      color: var(--muted);
      letter-spacing: 0.5px;
      margin-bottom: 6px;
    }
    .info-card p {
      font-size: 13px;
      color: var(--ink);
      font-family: 'JetBrains Mono', monospace;
    }

    .code-block {
      background: var(--code-bg);
      border: 1px solid var(--panel-border);
      border-radius: 6px;
      padding: 16px;
      font-family: 'JetBrains Mono', monospace;
      font-size: 12px;
      color: var(--teal);
      overflow-x: auto;
      line-height: 1.6;
      position: relative;
    }
    .copy-btn {
      position: absolute;
      top: 10px;
      right: 10px;
      background: rgba(255, 255, 255, 0.08);
      border: 1px solid var(--panel-border);
      color: var(--ink);
      font-size: 11px;
      padding: 4px 8px;
      border-radius: 4px;
      cursor: pointer;
    }
    .copy-btn:hover { background: var(--pink); color: #fff; }

    .data-table {
      width: 100%;
      border-collapse: collapse;
      font-size: 12px;
      background: var(--panel);
      border-radius: 8px;
      overflow: hidden;
      border: 1px solid var(--panel-border);
      margin-top: 16px;
    }
    .data-table th {
      background: var(--bg);
      padding: 12px 16px;
      text-align: left;
      font-family: 'Barlow Semi Condensed', sans-serif;
      font-size: 13px;
      color: var(--pink);
      border-bottom: 1px solid var(--panel-border);
    }
    .data-table td {
      padding: 12px 16px;
      border-bottom: 1px solid rgba(255, 255, 255, 0.04);
      color: var(--ink);
    }
    .data-table tr:hover td { background: rgba(255, 255, 255, 0.02); }

    .field-source { font-family: 'JetBrains Mono', monospace; color: var(--blue); font-size: 11px; }
    .field-target { font-family: 'JetBrains Mono', monospace; color: var(--pink); font-size: 11px; font-weight: 600; }
    .threat-tag { font-family: 'JetBrains Mono', monospace; color: var(--teal); font-size: 11px; }

    .trap-box {
      background: rgba(245, 198, 30, 0.05);
      border: 1px solid var(--amber);
      border-radius: 8px;
      padding: 20px;
      margin-top: 20px;
    }
    .trap-box h3 {
      color: var(--amber);
      font-size: 14px;
      margin-bottom: 8px;
      display: flex;
      align-items: center;
      gap: 8px;
      font-family: 'Barlow Semi Condensed', sans-serif;
    }
    .trap-box p {
      font-size: 13px;
      color: var(--ink);
      line-height: 1.6;
    }

    .pulsing-dot {
      width: 8px;
      height: 8px;
      background-color: var(--teal);
      border-radius: 50%;
      display: inline-block;
      box-shadow: 0 0 8px var(--teal);
      animation: pulse-dot 1.5s infinite;
    }
    @keyframes pulse-dot {
      0%, 100% { opacity: 0.6; transform: scale(0.9); }
      50% { opacity: 1; transform: scale(1.2); }
    }
  </style>
</head>
<body>

  <!-- Sidebar -->
  <aside class="sidebar">
    <div class="brand-header">
      <div class="brand-logo-wrap">
        __LOGO_SVG__
      </div>
      <div>
        <div class="brand-title">ABSTRACT SECURITY</div>
        <div class="brand-sub">GCP Architecture &amp; Diagnostics Suite</div>
      </div>
    </div>

    <div class="search-box">
      <input type="text" id="scenario-search" class="search-input" placeholder="Search architecture, WIF, BigQuery..." oninput="filterScenarios()">
    </div>

    <div class="scenario-list" id="sidebar-scenarios">
      <!-- Populated dynamically by JS -->
    </div>
  </aside>

  <!-- Main Area -->
  <main class="main">
    <!-- Topbar -->
    <header class="topbar">
      <div class="scenario-header">
        <h1 id="sc-title">
          <span class="pulsing-dot"></span>
          <span id="sc-title-text">Loading Architecture...</span>
        </h1>
        <p id="sc-subtitle">Telemetry pipeline and failure isolation reference</p>
      </div>

      <div class="actions-bar">
        <div class="hud-bar" id="hud-chips"></div>
        <button class="btn btn-secondary" onclick="openDrawioDesktop()">Launch Draw.io</button>
        <button class="btn btn-secondary" onclick="toggleFormat()" id="btn-format">View SVG</button>
        <a id="btn-dl" class="btn btn-primary" href="#" download>Export Asset</a>
      </div>
    </header>

    <!-- Navigation Tabs -->
    <nav class="nav-tabs">
      <button class="tab-btn active" id="tab-btn-arch" onclick="switchTab('arch')">1. Architecture &amp; Telemetry Flow</button>
      <button class="tab-btn" id="tab-btn-diag" onclick="switchTab('diag')">2. Diagnostic Runbook &amp; Traps</button>
      <button class="tab-btn" id="tab-btn-schema" onclick="switchTab('schema')">3. Schema Normalization &amp; SIEM Rules</button>
      <button class="tab-btn" id="tab-btn-tf" onclick="switchTab('tf')">4. Infrastructure as Code</button>
    </nav>

    <!-- Tab Content -->
    <div class="content-area">
      <!-- Tab 1: Architecture -->
      <div id="tab-arch" class="tab-pane active">
        <div class="info-grid" id="arch-specs-grid"></div>
        <div class="viewer-frame">
          <div class="viewer-toolbar">
            <span id="viewer-status">Viewing 2x Retina PNG</span>
            <div class="viewer-controls">
              <button class="tool-btn" onclick="zoomImage(1.2)">+ Zoom In</button>
              <button class="tool-btn" onclick="zoomImage(0.8)">- Zoom Out</button>
              <button class="tool-btn" onclick="resetZoom()">Reset</button>
            </div>
          </div>
          <div class="viewer-img-container">
            <img id="arch-img" class="viewer-img" src="" alt="Architecture Diagram">
          </div>
        </div>
      </div>

      <!-- Tab 2: Diagnostic Runbook -->
      <div id="tab-diag" class="tab-pane">
        <div style="max-width: 1000px; margin: 0 auto; display: flex; flex-direction: column; gap: 20px;">
          <h2 style="font-family: 'Barlow Semi Condensed', sans-serif; font-size: 20px; color: var(--pink);">
            ⚡ 5-Step Diagnostic &amp; Failure Isolation Runbook
          </h2>
          <div class="code-block" id="diag-steps-block">
            <button class="copy-btn" onclick="copyDiagSteps()">Copy All Commands</button>
            <pre id="diag-steps-text"></pre>
          </div>
          <div class="trap-box" id="diag-trap-box">
            <h3 id="trap-title">⚠️ THE #1 SILENT SINK FAILURE MODE</h3>
            <p id="trap-desc"></p>
            <div class="code-block" style="margin-top: 12px;">
              <button class="copy-btn" onclick="copyText('trap-fix')">Copy Fix</button>
              <pre id="trap-fix" style="color: var(--amber);"></pre>
            </div>
          </div>
        </div>
      </div>

      <!-- Tab 3: Schema Normalization -->
      <div id="tab-schema" class="tab-pane">
        <div style="max-width: 1100px; margin: 0 auto;">
          <h2 style="font-family: 'Barlow Semi Condensed', sans-serif; font-size: 20px; color: var(--pink); margin-bottom: 12px;">
            🛡️ Schema Normalization Contract (Raw Protobuf ➔ Abstract ACS / ECS)
          </h2>
          <table class="data-table">
            <thead>
              <tr>
                <th>GCP Raw Protobuf Field</th>
                <th>Abstract ACS / ECS Target</th>
                <th>Normalization Description</th>
                <th>SIEM Threat Utility</th>
              </tr>
            </thead>
            <tbody id="schema-tbody"></tbody>
          </table>

          <div style="margin-top: 30px;">
            <h3 style="font-family: 'Barlow Semi Condensed', sans-serif; font-size: 16px; color: var(--teal); margin-bottom: 8px;" id="rule-title">
              Actionable SIEM Detection Rule
            </h3>
            <div class="code-block">
              <button class="copy-btn" onclick="copyText('rule-kql')">Copy KQL</button>
              <pre id="rule-kql" style="color: var(--teal);"></pre>
            </div>
            <div class="code-block" style="margin-top: 12px;">
              <button class="copy-btn" onclick="copyText('rule-sql')">Copy BigQuery SQL</button>
              <pre id="rule-sql" style="color: var(--blue);"></pre>
            </div>
          </div>
        </div>
      </div>

      <!-- Tab 4: Terraform Code -->
      <div id="tab-tf" class="tab-pane">
        <div style="max-width: 1000px; margin: 0 auto;">
          <h2 style="font-family: 'Barlow Semi Condensed', sans-serif; font-size: 20px; color: var(--pink); margin-bottom: 12px;">
            📦 OpenTofu / Terraform Module Definition
          </h2>
          <div class="code-block">
            <button class="copy-btn" onclick="copyText('tf-code')">Copy Terraform</button>
            <pre id="tf-code" style="color: var(--pink);"></pre>
          </div>
        </div>
      </div>
    </div>
  </main>

  <script>
    const scenarios = __SCENARIOS_JSON__;
    let currentScId = '01-logging-project';
    let currentFormat = 'png';
    let zoomLevel = 1.0;

    function init() {
      renderSidebar();
      selectScenario('01-logging-project');
    }

    function renderSidebar(filteredScenarios = null) {
      const container = document.getElementById('sidebar-scenarios');
      container.innerHTML = '';
      const scList = filteredScenarios || Object.values(scenarios);

      // Group by category
      const categories = {};
      scList.forEach(sc => {
        if (!categories[sc.category]) categories[sc.category] = [];
        categories[sc.category].push(sc);
      });

      for (const [catName, items] of Object.entries(categories)) {
        const catHeader = document.createElement('div');
        catHeader.className = 'category-title';
        catHeader.innerText = catName;
        container.appendChild(catHeader);

        items.forEach(sc => {
          const item = document.createElement('div');
          item.className = 'scenario-item' + (sc.id === currentScId ? ' active' : '');
          item.id = 'sc-nav-' + sc.id;
          item.onclick = () => selectScenario(sc.id);
          item.innerHTML = `
            <div class="scenario-name">
              <span>${sc.title.split('·')[1] || sc.title}</span>
            </div>
            <span class="scenario-tag">${sc.num}</span>
          `;
          container.appendChild(item);
        });
      }
    }

    function selectScenario(id) {
      currentScId = id;
      const sc = scenarios[id];
      if (!sc) return;

      // Update sidebar active state
      document.querySelectorAll('.scenario-item').forEach(el => el.classList.remove('active'));
      const activeNav = document.getElementById('sc-nav-' + id);
      if (activeNav) activeNav.classList.add('active');

      // Update Header
      document.getElementById('sc-title-text').innerText = sc.title;
      document.getElementById('sc-subtitle').innerText = sc.subtitle;

      // Update HUD Chips
      const hudContainer = document.getElementById('hud-chips');
      hudContainer.innerHTML = '';
      (sc.chips || []).forEach(chip => {
        const chipEl = document.createElement('div');
        chipEl.className = `hud-chip ${chip.tone}`;
        chipEl.innerText = chip.text;
        hudContainer.appendChild(chipEl);
      });

      // Update Image & Buttons
      updateImageSrc();

      // Update Tab 1 Specs
      const grid = document.getElementById('arch-specs-grid');
      grid.innerHTML = `
        <div class="info-card"><h4>Telemetry Category</h4><p>${sc.specs.logNames}</p></div>
        <div class="info-card"><h4>Transport Protocol</h4><p>${sc.specs.protocol}</p></div>
        <div class="info-card"><h4>Ingest Latency SLA</h4><p>${sc.specs.latency}</p></div>
        <div class="info-card"><h4>Peak Throughput</h4><p>${sc.specs.throughput}</p></div>
      `;

      // Update Tab 2 Diagnostics
      const diag = sc.diagnostics;
      let allCommands = '';
      let diagHtml = '';
      diag.steps.forEach(st => {
        allCommands += `# ${st.num}. ${st.title}\\n${st.cmd}\\n\\n`;
        diagHtml += `# STEP ${st.num}: ${st.title}\\n${st.cmd}\\n\\n`;
      });
      document.getElementById('diag-steps-text').innerText = diagHtml;
      document.getElementById('trap-title').innerText = diag.trapTitle;
      document.getElementById('trap-desc').innerText = diag.trapDesc;
      document.getElementById('trap-fix').innerText = diag.trapFix;

      // Update Tab 3 Schema
      const tbody = document.getElementById('schema-tbody');
      tbody.innerHTML = '';
      sc.schema.fields.forEach(f => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td class="field-source">${f.raw}</td>
          <td class="field-target">${f.acs}</td>
          <td>${f.desc}</td>
          <td class="threat-tag">${f.util}</td>
        `;
        tbody.appendChild(tr);
      });
      document.getElementById('rule-title').innerText = sc.schema.ruleTitle;
      document.getElementById('rule-kql').innerText = sc.schema.ruleKql;
      document.getElementById('rule-sql').innerText = sc.schema.ruleSql;

      // Update Tab 4 Terraform
      document.getElementById('tf-code').innerText = sc.terraform;
    }

    function switchTab(tabId) {
      document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
      document.querySelectorAll('.tab-pane').forEach(pane => pane.classList.remove('active'));

      const activeBtn = document.getElementById('tab-btn-' + tabId);
      if (activeBtn) activeBtn.classList.add('active');
      const activePane = document.getElementById('tab-' + tabId);
      if (activePane) activePane.classList.add('active');
    }

    function updateImageSrc() {
      const sc = scenarios[currentScId];
      if (!sc) return;
      const imgEl = document.getElementById('arch-img');
      const dlBtn = document.getElementById('btn-dl');
      const formatBtn = document.getElementById('btn-format');
      const statusText = document.getElementById('viewer-status');

      if (currentFormat === 'svg') {
        imgEl.src = sc.imgSvg;
        dlBtn.href = sc.imgSvg;
        dlBtn.innerText = 'Export Vector SVG';
        formatBtn.innerText = 'Switch to 2x PNG';
        statusText.innerText = 'Viewing Lossless Vector SVG';
      } else {
        imgEl.src = sc.imgPng;
        dlBtn.href = sc.imgPng;
        dlBtn.innerText = 'Export 2x PNG';
        formatBtn.innerText = 'Switch to Vector SVG';
        statusText.innerText = 'Viewing 2x Retina PNG';
      }
    }

    function toggleFormat() {
      currentFormat = (currentFormat === 'png') ? 'svg' : 'png';
      updateImageSrc();
    }

    function zoomImage(factor) {
      zoomLevel *= factor;
      if (zoomLevel < 0.4) zoomLevel = 0.4;
      if (zoomLevel > 3.0) zoomLevel = 3.0;
      document.getElementById('arch-img').style.transform = `scale(${zoomLevel})`;
    }

    function resetZoom() {
      zoomLevel = 1.0;
      document.getElementById('arch-img').style.transform = 'scale(1.0)';
    }

    function openDrawioDesktop() {
      const sc = scenarios[currentScId];
      if (sc) {
        prompt('Copy and run this command in terminal to edit in Draw.io Desktop:', `./scripts/open-diagram.sh ${sc.drawio}`);
      }
    }

    function copyText(elemId) {
      const text = document.getElementById(elemId).innerText;
      navigator.clipboard.writeText(text);
      alert('Copied to clipboard!');
    }

    function copyDiagSteps() {
      const text = document.getElementById('diag-steps-text').innerText;
      navigator.clipboard.writeText(text);
      alert('All diagnostic steps copied to clipboard!');
    }

    function filterScenarios() {
      const query = document.getElementById('scenario-search').value.toLowerCase();
      const filtered = Object.values(scenarios).filter(sc => {
        return sc.title.toLowerCase().includes(query) ||
               sc.subtitle.toLowerCase().includes(query) ||
               sc.category.toLowerCase().includes(query) ||
               sc.id.toLowerCase().includes(query);
      });
      renderSidebar(filtered);
    }

    window.onload = init;
  </script>
</body>
</html>
"""

def main():
    print(f"Generating {OUT_HTML}...")
    scenarios_json = json.dumps(SCENARIOS_DATA, indent=2)
    rendered = HTML_TEMPLATE.replace("__LOGO_SVG__", LOGO_SVG).replace("__SCENARIOS_JSON__", scenarios_json)
    OUT_HTML.write_text(rendered, encoding="utf-8")
    print(f"SUCCESS: Generated {OUT_HTML} ({len(rendered)} bytes) covering all 16 scenarios!")

if __name__ == "__main__":
    main()
