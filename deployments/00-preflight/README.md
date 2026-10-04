<picture>
  <source media="(prefers-color-scheme: dark)" srcset="../../brand/abstract-logo-white.svg">
  <img alt="Abstract Security" src="../../brand/abstract-logo-black.svg" width="180">
</picture>

# Preflight Readiness Assessment

<a href="https://shell.cloud.google.com/cloudshell/editor?cloudshell_git_repo=https://github.com/IamABS3C/abstract-gcp-templates&cloudshell_git_branch=main&cloudshell_workspace=deployments/00-preflight&cloudshell_tutorial=TUTORIAL.md"><img alt="Open in Cloud Shell" src="https://gstatic.com/cloudssh/images/open-btn.svg" height="24"></a>

Read-only environmental inspection assessing permissions, quotas, and organizational hierarchy readiness before deploying Abstract Security infrastructure.

---

## Why Preflight Readiness Matters

Terraform fails at **apply time** when permissions are missing—often *after* it has already provisioned topics or service accounts. The preflight check inspects your environment beforehand and is **100% read-only**, making it safe to execute in production or during live architecture reviews.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          Preflight Inspection Phase                         │
│                                                                             │
│   • Organization & Folder Hierarchy Discovery                               │
│   • Caller Identity & IAM Role Evaluation at Org/Billing Scopes             │
│   • Billing Account Status & Cloud Build Readiness                          │
│   • Existing Log Sinks & Potential Collision Detection                      │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ Assessment Report
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                             Actionable Outcomes                             │
│                                                                             │
│   ✅ Ready for Organization-Wide Aggregated Sink (02-audit-logs-organization)│
│   ⚠️ Missing roles/logging.configWriter (Requires Org Admin grant)          │
│   ℹ️ Standalone project scope required (Sandbox / Pilot path)               │
└─────────────────────────────────────────────────────────────────────────────┘
```

```mermaid
flowchart TD
    subgraph Preflight["Preflight Discovery (scripts/preflight.sh)"]
        CheckOrg["Check Organization ID & IAM Roles"]
        CheckBilling["Check Billing Status & Quotas"]
        CheckSinks["Inspect Existing Log Sinks & Collisions"]
    end

    subgraph Decisions["Readiness Assessment"]
        OrgReady{"Org Admin IAM Granted?"}
        BillingReady{"Billing Account Open?"}
    end

    subgraph Pathways["Recommended Deployment Pathway"]
        DeployOrg["02-audit-logs-organization<br/>(Full Production Aggregated Sink)"]
        DeployPilot["02-audit-logs-project<br/>(Single Project Pilot Evaluation)"]
        FixIAM["Request roles/logging.configWriter<br/>at Organization Root"]
    end

    CheckOrg --> OrgReady
    CheckBilling --> BillingReady
    CheckSinks --> OrgReady

    OrgReady -->|Yes| DeployOrg
    OrgReady -->|No| FixIAM
    FixIAM -.->|Temporary fallback| DeployPilot

    style Preflight fill:#f8f9fa,stroke:#4285F4,stroke-width:1.5px
    style DeployOrg fill:#FF216B,color:#ffffff,stroke:#FF216B,stroke-width:2px
    style DeployPilot fill:#f8f9fa,stroke:#FBBC04,stroke-width:1.5px
```

---

## How to Run the Preflight Check

From the repository root:

```bash
./scripts/preflight.sh
```

Or pass explicit context:

```bash
./scripts/preflight.sh --org-id="123456789012" --project="acme-security-logging"
```

---

[← All scenarios](../../README.md) · [Architecture](../../docs/ARCHITECTURE.md) · [Bootstrap Logging Project](../01-logging-project/README.md)
