<picture>
  <source media="(prefers-color-scheme: dark)" srcset="../../brand/abstract-logo-white.svg">
  <img alt="Abstract Security" src="../../brand/abstract-logo-black.svg" width="180">
</picture>

# Billing Account Audit Log Export

<a href="https://shell.cloud.google.com/cloudshell/editor?cloudshell_git_repo=https://github.com/IamABS3C/abstract-gcp-templates&cloudshell_git_branch=main&cloudshell_workspace=deployments/10-billing-account&cloudshell_tutorial=TUTORIAL.md"><img alt="Open in Cloud Shell" src="https://gstatic.com/cloudssh/images/open-btn.svg" height="24"></a>

Export Cloud Billing Account audit logs directly to **Abstract Security** via Cloud Pub/Sub.

<p align="center">
  <img src="../../images/diagrams/10-billing-account.png" width="100%" alt="GCP Billing Account Out-of-Hierarchy Audit Pipeline Architecture Diagram">
</p>

> [!TIP]
> **Interactive Architecture Diagram (Draw.io / diagrams.net)**:
> Edit, export, and customize this architecture directly on your machine or browser:
> ```bash
> ./scripts/open-diagram.sh 10-billing-account          # Opens in macOS Draw.io Desktop
> ./scripts/open-diagram.sh 10-billing-account --web    # Opens in diagrams.net
> ```

---

## Why Billing Account Logs Sit Outside the Hierarchy

In Google Cloud, the resource hierarchy is strictly structured as **Organization &rarr; Folders &rarr; Projects &rarr; Resources**.

Aggregated log sinks created at the organization level (`sink_scope = "organization"` with `include_children = true`) or folder level capture log events from every project and folder contained within that scope. However, **Cloud Billing Accounts sit outside the resource hierarchy entirely**. They are root-level billing entities associated with organizations and projects, not child nodes within them.

As a result:
* An organization-level aggregated sink **does NOT capture billing account audit logs**.
* A folder-level or project-level sink **does NOT capture billing account audit logs**.

### Security Significance of Billing Account Audit Logs

Billing accounts represent critical administrative and financial control planes. Audit logs from billing accounts capture high-impact security events, including:

1. **Billing IAM changes**: Adding or modifying roles such as `roles/billing.admin`, `roles/billing.user`, or `roles/billing.viewer`. Unauthorized privilege escalation here can allow attackers to hijack billing profiles or attach rogue projects.
2. **Project billing association and disassociation**: Linking malicious or hijacked projects to your billing account (e.g., to fund cryptomining), or detaching billing from legitimate production projects (which immediately halts paid APIs and compute workloads).
3. **Budget and alert modifications**: Disabling, raising, or deleting spend alert thresholds or Pub/Sub notification channels, masking unexpected cost surges from compromise.
4. **Payment profile modifications**: Changes to payment methods, billing contact addresses, or invoicing settings.

To monitor these events, a dedicated `google_logging_billing_account_sink` must be created directly on the Cloud Billing Account.

```
┌───────────────────────────────────────────────┐      ┌────────────────────────────────────────────────────────┐
│         GCP Resource Hierarchy (Org Sink)     │      │        Billing Account (Outside Hierarchy)             │
│                                               │      │                                                        │
│  Organization: organizations/123456789012     │      │  Billing Account: billingAccounts/012345-567890-ABCDEF │
│       │                                       │      │   • IAM policy changes (roles/billing.admin)           │
│       ├── Folder: Production                  │      │   • Project link/unlink (cryptomining/hijacking)       │
│       │     └── Workload Project A            │      │   • Budget alert modifications                         │
│       └── Folder: Development                 │      └───────────────────────────┬────────────────────────────┘
│             └── Workload Project B            │                                  │ Dedicated Billing Sink
│                                               │                                  │ (google_logging_billing_account_sink)
│  (Org Aggregated Sink CANNOT see billing logs)│                                  ▼
└───────────────────────────────────────────────┘      ┌────────────────────────────────────────────────────────┐
                                                       │        Dedicated Logging Project (log_project)         │
                                                       │                                                        │
                                                       │   Pub/Sub Topic: abstract-billing-audit-logs           │
                                                       │         │                                              │
                                                       │         ▼                                              │
                                                       │   Pub/Sub Pull Subscription: ...-sub                   │
                                                       └───────────────────────────┬────────────────────────────┘
                                                                                   │ Authenticated Pull
                                                                                   ▼
                                                       ┌────────────────────────────────────────────────────────┐
                                                       │               Abstract Security Platform               │
                                                       │                                                        │
                                                       │   Financial & Administrative Control-Plane SIEM        │
                                                       └────────────────────────────────────────────────────────┘
```

```mermaid
flowchart TD
    subgraph Hierarchy["GCP Resource Hierarchy (Covered by Org Sinks)"]
        Org["Organization: organizations/..."]
        Folder["Folders: Production / Staging"]
        Project["Workload Projects"]
        Org --> Folder --> Project
    end

    subgraph BillingPlane["Root Billing Entity (Outside Hierarchy)"]
        BillingAccount["Cloud Billing Account<br/>billingAccounts/..."]
        BillingEvents["• IAM modifications<br/>• Project link / unlink<br/>• Budget / alert changes"]
        BillingAccount --- BillingEvents
    end

    subgraph SinkPipeline["Dedicated Logging Project"]
        BillingSink["Billing Account Log Sink<br/>(google_logging_billing_account_sink)"]
        Topic["Pub/Sub Topic<br/>abstract-billing-audit-logs"]
        Sub["Pub/Sub Pull Subscription<br/>abstract-billing-audit-logs-sub"]
        SA["Reader Service Account<br/>abstract-billing-reader"]
    end

    subgraph Abstract["Abstract Security Platform"]
        AbstractSIEM["Abstract Security SIEM"]
    end

    Hierarchy -.->|NOT captured by Org Sinks| BillingAccount
    BillingAccount -->|Captures Billing Audit Events| BillingSink
    BillingSink -->|Writer Identity (roles/pubsub.publisher)| Topic
    Topic --> Sub
    SA -->|roles/pubsub.subscriber| Sub
    Sub --> AbstractSIEM

    style Abstract fill:#FF216B15,stroke:#FF216B,stroke-width:2px
    style AbstractSIEM fill:#FF216B,color:#ffffff,stroke:#FF216B,stroke-width:2px
    classDef billingBox fill:#f8f9fa,stroke:#EA4335,stroke-width:1.5px;
    classDef gcpBox fill:#f8f9fa,stroke:#4285F4,stroke-width:1.5px;
    class BillingPlane billingBox;
    class Hierarchy,SinkPipeline gcpBox;
```

---

## Telemetry Dataflow & Ingestion Path

Billing audit telemetry flows via write-time evaluation from the Billing Account Log Router directly to Pub/Sub:

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                 TELEMETRY DATAFLOW & INGESTION PATH                                     │
│                                                                                                         │
│   Billing Account Log Router           Pub/Sub Ingestion Topic               Abstract Security SIEM     │
│   ┌───────────────────────────┐        ┌───────────────────────────┐         ┌────────────────────────┐ │
│   │ Billing Account Sink      │  gRPC  │ Pub/Sub Topic:            │  gRPC   │ Abstract Ingestion     │ │
│   │ • Admin Activity          ├───────►│ abstract-billing-audit-log├────────►│ • IAM Drift Monitoring │ │
│   │ • System Events           │ TLS 1.3│ Sub: ...-logs-sub         │ TLS 1.3 │ • Hijack Detection     │ │
│   └───────────────────────────┘        └───────────────────────────┘         └────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### Technical Telemetry Parameters

| Dimension | Specification | Operational Note |
|---|---|---|
| **Ingestion Protocols** | Google Internal Log Router Dispatcher ➔ Cloud Pub/Sub StreamingPull (gRPC / TLS 1.3) | Direct streaming with zero polling |
| **Transport Port** | `443` (Outbound TLS) | Industry-standard cryptographic isolation |
| **Propagation Delay** | 3 to 5 minutes post-creation | Write-time evaluation rule applies; early test events do not backfill |
| **Streaming Latency** | 1 to 3 seconds under steady state | Events reach Pub/Sub moments after API call commit |
| **Throughput & Capacity** | 1–100 events/day typical, burst capacity 1,000+ eps | Low volume, ultra-high criticality stream |
| **Durability & Guarantees** | At-least-once delivery, 7-day retention buffer | Guarantees non-repudiation of financial operations |

---

## What Gets Created

* **Cloud Logging Billing Sink**: A sink bound directly to your Billing Account routing `admin_activity` and `system_event` logs to Cloud Pub/Sub.
* **Pub/Sub Topic & Subscription**: Dedicated topic (`abstract-billing-audit-logs`) and pull subscription (`abstract-billing-audit-logs-sub`) in your logging project.
* **Sink Writer IAM Binding**: Grants `roles/pubsub.publisher` on the topic to the billing sink's unique writer identity service account.
* **Abstract Pull Identity**: Dedicated service account (`abstract-billing-reader`) granted `roles/pubsub.subscriber` on the subscription only.

---

## Diagnostic & Troubleshooting Decision Tree

Follow this structured protocol to diagnose and isolate billing account audit export issues:

```
Billing Account Audit Export Issue
  │
  ├──► [Billing Sink Configured on Billing Account?]
  │      ├── NO  ──► Check billing sinks via gcloud
  │      │           Command: gcloud logging sinks list --billing-account=BILLING_ID
  │      └── YES ──► Check Topic IAM Permissions
  │
  ├──► [Sink Writer Identity Has roles/pubsub.publisher?]
  │      ├── NO  ──► Missing Publisher Binding on Destination Topic (The #1 Billing Trap!)
  │      │           Identity: service-billing-NUM@gcp-sa-logging.iam.gserviceaccount.com
  │      │           Remediation: gcloud pubsub topics add-iam-policy-binding ...
  │      └── YES ──► Check Propagation Window & Error Logs
  │
  ├──► [Did You Wait 5 Minutes After Apply?]
  │      ├── NO  ──► Sinks evaluate at WRITE TIME. Events during the first 3 mins drop!
  │      │           Wait 5 minutes and test with a benign billing update (e.g. description edit).
  │      └── YES ──► Check Sink Errors
  │
  └──► [Sink Errors in Logging Project?]
         └── YES ──► Query logName:"logging.googleapis.com%2Fsink_error"
                     Verify permission denied or destination project quotas.
```

### Verification & Remediation Commands

#### 1. Verify Billing Account Sink
```bash
export BILLING_ACCOUNT_ID="012345-567890-ABCDEF"
gcloud logging sinks describe abstract-billing-audit-sink \
  --billing-account="$BILLING_ACCOUNT_ID" \
  --format="yaml(name,destination,filter,writerIdentity)"
```

#### 2. Verify Writer Identity Publisher Permissions
```bash
export LOG_PROJECT="acme-security-logging"
export WRITER_SA=$(gcloud logging sinks describe abstract-billing-audit-sink \
  --billing-account="$BILLING_ACCOUNT_ID" \
  --format="value(writerIdentity)")

echo "Billing Sink Writer Identity: $WRITER_SA"

# Check publisher binding on topic
gcloud pubsub topics get-iam-policy abstract-billing-audit-logs \
  --project="$LOG_PROJECT" \
  --flatten="bindings[].members" \
  --filter="bindings.role:roles/pubsub.publisher"
```

If missing, grant publisher role:
```bash
gcloud pubsub topics add-iam-policy-binding abstract-billing-audit-logs \
  --project="$LOG_PROJECT" \
  --member="${WRITER_SA}" \
  --role="roles/pubsub.publisher"
```

#### 3. Check for Sink Delivery Errors
```bash
gcloud logging read 'logName:"logging.googleapis.com%2Fsink_error"' \
  --project="$LOG_PROJECT" \
  --limit=20
```

#### 4. Pull Test Billing Messages
```bash
gcloud pubsub subscriptions pull abstract-billing-audit-logs-sub \
  --project="$LOG_PROJECT" \
  --limit=2
```

---

## Permissions Needed

Setting up a billing account sink spans two permission boundaries: the billing account itself and the logging project.

### 1. On the Billing Account

You need **`roles/logging.configWriter` (Logs Configuration Writer)** directly on the billing account.

> [!IMPORTANT]
> `roles/resourcemanager.organizationAdmin` or Project `roles/owner` does **NOT** grant permissions to create sinks on a billing account unless explicit billing permissions have been assigned.

#### Grant the Required Role:
```bash
gcloud billing accounts add-iam-policy-binding "$BILLING_ACCOUNT_ID" \
  --member="user:security-admin@example.com" \
  --role="roles/logging.configWriter"
```

### 2. On the Logging Project

In the dedicated logging project hosting Pub/Sub:
* `roles/pubsub.admin` — To create the topic, subscription, and assign IAM roles.
* `roles/resourcemanager.projectIamAdmin` (or `roles/iam.serviceAccountAdmin` + Pub/Sub IAM admin) — To bind the sink's writer identity and configure the pull service account.
* `roles/serviceusage.serviceUsageAdmin` — To enable required APIs (`pubsub.googleapis.com`, `logging.googleapis.com`).

---

## How to Plan and Apply

### Step 1 — Clone and Navigate

```bash
cd deployments/10-billing-account
```

### Step 2 — Configure Variables

```bash
export BILLING_ACCOUNT_ID=$(gcloud billing accounts list --format='value(name.basename())' --limit=1)
export LOG_PROJECT="acme-security-logging"

cat > terraform.tfvars <<EOF
billing_account_id = "$BILLING_ACCOUNT_ID"
log_project        = "$LOG_PROJECT"
EOF
```

### Step 3 — Apply

```bash
tofu init
tofu plan
tofu apply
```

### Step 4 — Verify Outputs

```bash
tofu output abstract_onboarding
```

---

[← All scenarios](../../README.md) · [Architecture](../../docs/ARCHITECTURE.md) · [Permissions](../../docs/PERMISSIONS.md) · [Filters](../../docs/FILTERS.md)
