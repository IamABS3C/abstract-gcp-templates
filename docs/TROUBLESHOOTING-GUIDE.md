<picture>
  <source media="(prefers-color-scheme: dark)" srcset="../brand/abstract-logo-white.svg">
  <img alt="Abstract Security" src="../brand/abstract-logo-black.svg" width="180">
</picture>

# Master Troubleshooting & Diagnostic Runbook

This guide is the definitive, battle-tested diagnostic reference for all Google Cloud to Abstract Security telemetry pipelines. It details the systematic 5-step diagnostic protocol, isolates failure points across all 14 architectural scenarios, and provides copy-paste `gcloud` verification and remediation commands.

---

## The 5-Step Diagnostic Protocol

Every telemetry failure—whether a silent log drop, quota throttle, or schema parser error—can be isolated using this sequential 5-step protocol:

```
[ Step 1: Ingestion ] ➔ [ Step 2: Sink Config ] ➔ [ Step 3: Topic IAM ] ➔ [ Step 4: Subscription ] ➔ [ Step 5: Abstract Lake ]
   gcloud logging         gcloud logging sinks     gcloud pubsub topics     gcloud pubsub subs       Abstract SIEM UI
     read 'logName:*'          describe SINK         get-iam-policy TOPIC     pull PROBE sub           Logs -> vendor: GCP
```

---

### Step 1: Source Workload & Cloud Logging Verification

**Question:** Are the source GCP services generating log entries into Cloud Logging?

```bash
# Test for recent Admin Activity audit logs in the source project
gcloud logging read 'logName:"logs/cloudaudit.googleapis.com%2Factivity"' \
  --project="SOURCE_PROJECT_ID" \
  --limit=3 \
  --format="table(timestamp,protoPayload.methodName,protoPayload.authenticationInfo.principalEmail)"
```

* **PASS:** Output displays recent events (e.g. `SetIamPolicy`, `CreateProject`). Proceed to Step 2.
* **FAIL (Zero rows returned):**
  * The source service API may be disabled.
  * Workload is idle or generating no mutating events.
  * If testing Data Access logs (`data_access`), verify that `auditConfigs` is enabled in IAM policies (see Scenario 03).

---

### Step 2: Log Router Sink Configuration & Hierarchy Inheritance

**Question:** Is the Log Router Sink correctly configured, and does it include child resources if scoped at Organization or Folder level?

```bash
# Describe the organization-level sink
gcloud logging sinks describe abstract-org-audit-sink \
  --organization="ORG_ID" \
  --format="yaml(name,destination,filter,includeChildren,writerIdentity)"
```

* **PASS:** `destination` matches `pubsub.googleapis.com/projects/.../topics/...`, `includeChildren` is `True`, and a non-empty `writerIdentity` is present.
* **FAIL (includeChildren is False or omitted):**
  * **Critical Blind Spot:** Sinks without `--include-children` capture ONLY events generated on the Organization resource itself. All folders and projects are 100% blind.
  * **Remediation:**
    ```bash
    gcloud logging sinks update abstract-org-audit-sink \
      --organization="ORG_ID" \
      --include-children
    ```

---

### Step 3: Sink Writer Identity & Pub/Sub Topic Permissions (The #1 Silent Failure Trap)

**Question:** Does the unique service account generated for the sink (`writerIdentity`) hold `roles/pubsub.publisher` on the destination Pub/Sub topic?

```bash
# 1. Extract the sink's unique writer identity
WRITER_SA=$(gcloud logging sinks describe abstract-org-audit-sink \
  --organization="ORG_ID" \
  --format="value(writerIdentity)")

echo "Sink Writer Service Account: ${WRITER_SA}"

# 2. Inspect the IAM policy on the destination Pub/Sub topic
gcloud pubsub topics get-iam-policy abstract-audit-logs \
  --project="LOGGING_PROJECT_ID" \
  --flatten="bindings[].members" \
  --filter="bindings.role:roles/pubsub.publisher" \
  --format="table(bindings.role,bindings.members)"
```

* **PASS:** `${WRITER_SA}` is explicitly listed with `roles/pubsub.publisher`.
* **FAIL (The #1 Silent Trap in GCP Logging):**
  * When an aggregated sink is created, Google Cloud automatically provisions a dedicated service account formatted as:
    `serviceAccount:service-org-ORG_NUM@gcp-sa-logging.iam.gserviceaccount.com` (or `service-PROJECT_NUM...` for project sinks).
  * **This service account holds ZERO permissions by default!**
  * The Log Router will silently drop 100% of logs. There is no warning in the GCP Console, and no error logged to the project.
  * **Immediate Remediation:**
    ```bash
    gcloud pubsub topics add-iam-policy-binding abstract-audit-logs \
      --project="LOGGING_PROJECT_ID" \
      --member="${WRITER_SA}" \
      --role="roles/pubsub.publisher"
    ```

---

### Step 4: Pub/Sub Subscription Delivery & Backlog Verification

**Question:** Are messages arriving on the topic and ready to be consumed by the pull subscription?

```bash
# 1. Inspect subscription backlog and unacked message age
gcloud monitoring metrics list \
  --filter="metric.type:pubsub.googleapis.com/subscription/num_undelivered_messages"

# 2. Prove delivery on a probe subscription from Cloud Shell
# Never pull from abstract-audit-logs-sub: with --auto-ack that deletes events before Abstract
# reads them, and without it hides them from Abstract for the ack deadline.
# Pull from a throwaway subscription on the same topic instead. Create it BEFORE the
# test event: a new subscription only receives messages published after it exists.
PROBE="abstract-probe-$(date +%s)"
gcloud pubsub subscriptions create "$PROBE" --topic=abstract-audit-logs \
  --project="LOGGING_PROJECT_ID" --expiration-period=1d --message-retention-duration=10m
# Fire a fresh Admin Activity event inside the sink's scope, then wait for routing.
gcloud pubsub topics create "$PROBE" --project="LOGGING_PROJECT_ID" --quiet
gcloud pubsub topics delete "$PROBE" --project="LOGGING_PROJECT_ID" --quiet
sleep 75
gcloud pubsub subscriptions pull "$PROBE" --project="LOGGING_PROJECT_ID" --limit=1 --auto-ack
gcloud pubsub subscriptions delete "$PROBE" --project="LOGGING_PROJECT_ID" --quiet
```

* **PASS:** The probe pull returns a valid Cloud Audit Log JSON message with base64 payload.
* **FAIL:**
  * If `PERMISSION_DENIED`: The caller or ingestion service account lacks `roles/pubsub.subscriber` on the subscription.
  * If `num_undelivered_messages` is accumulating steadily: The Abstract subscriber worker is disconnected, rate-limited, or token expired.

---

### Step 5: Abstract Security Ingestion & Normalizer Verification

**Question:** Are raw events parsed into normalized Elastic Common Schema (ECS) / Abstract Common Schema (ACS) and indexed into search?

1. Open the **Abstract Security Platform Console**.
2. Navigate to **Data Lake ➔ Logs ➔ Live Tail**.
3. Apply filter: `vendor: "GCP"` or `event.dataset: "gcp.audit_logs"`.
4. Verify that fields like `user.email`, `event.action`, `source.ip`, and `threat.score` are populated.

* **FAIL (Raw message visible but unparsed):**
  * Schema definition update required in `parsers/`.
  * Ensure the parser regex matches the incoming `protoPayload.methodName`.

---

## Scenario-by-Scenario Diagnostic Runbooks

### Scenario 01: Centralized Logging Project
| Symptom | Root Cause | Verification Command | Solution |
|---|---|---|---|
| Pub/Sub publish quota errors (`RESOURCE_EXHAUSTED`) | Regional publish throughput exceeded in destination project | `gcloud monitoring metrics list --filter="metric.type:pubsub.googleapis.com/topic/byte_publish_utilization"` | Request quota increase or partition extreme-tier logs to a dedicated project |
| Messages routed to Dead-Letter Queue (DLQ) | Message size > 10MB or schema incompatibility | `gcloud pubsub subscriptions pull abstract-audit-logs-dlq --limit=1` | Inspect failed payload; adjust dead-letter delivery attempts |
| CMEK key decryption errors | Cloud KMS service agent missing `roles/cloudkms.cryptoKeyEncrypterDecrypter` | `gcloud kms keys get-iam-policy KEY_NAME --keyring=RING --location=LOC` | Grant KMS Decrypter role to `service-PROJECT_NUM@gcp-sa-pubsub.iam.gserviceaccount.com` |

---

### Scenario 02: Org & Folder Aggregated Sinks
| Symptom | Root Cause | Verification Command | Solution |
|---|---|---|---|
| New projects created in org do not stream logs | `--include-children` omitted on sink | `gcloud logging sinks describe SINK_NAME --organization=ORG_ID --format="value(includeChildren)"` | Run `gcloud logging sinks update SINK_NAME --include-children` |
| Sibling folders not monitored | Folder sink applied instead of Org sink | `gcloud logging sinks describe SINK_NAME --folder=FOLDER_ID` | Either apply Org sink or deploy individual folder sinks across each tenant subtree |
| `PERMISSION_DENIED` applying sink | User lacks `roles/logging.configWriter` at Organization level | `gcloud organizations get-iam-policy ORG_ID` | Contact Organization Admin to run Terraform or grant role |

---

### Scenario 03: Data Access Logs (BigQuery & Storage)
| Symptom | Root Cause | Verification Command | Solution |
|---|---|---|---|
| No BigQuery query queries or table reads appear | `auditConfigs` for `DATA_READ` / `DATA_WRITE` disabled by default | `gcloud organizations get-iam-policy ORG_ID --filter="auditConfigs"` | Deploy `deployments/03-data-access` or update IAM policy with `allServices` auditConfig |
| Massive bill shock from logging egress | Internal service polling / heartbeats ingested without exclusion | `gcloud logging sinks describe SINK_NAME --format="value(exclusions)"` | Apply exclusion filter: `protoPayload.serviceData.jobGetQueryResultsResponse:*` and `callerIp="130.211.0.0/22"` |

---

### Scenario 04: Google Workspace & Identity
| Symptom | Root Cause | Verification Command | Solution |
|---|---|---|---|
| User login events (`loginSuccess`) missing from GCP Cloud Logging | Native Cloud Audit Logs Sharing disabled in Google Workspace Admin Console | `gcloud logging read 'protoPayload.serviceName:"login.googleapis.com"' --organization=ORG_ID --limit=1` | Go to `admin.google.com ➔ Account Settings ➔ Legal and compliance ➔ Sharing options ➔ Google Cloud Platform ➔ Enable` |
| Domain-Wide Delegation 401 Unauthorized | Service Account client ID not authorized in Google Workspace API Controls | `admin.google.com ➔ Security ➔ Access and data control ➔ API controls ➔ Domain-wide delegation` | Authorize Service Account Client ID with OAuth scope `https://www.googleapis.com/auth/admin.reports.audit.readonly` |

---

### Scenario 06: Security Command Center (SCC)
| Symptom | Root Cause | Verification Command | Solution |
|---|---|---|---|
| Findings visible in SCC UI but never reach Pub/Sub | SCC Service Agent lacks `roles/pubsub.publisher` on destination topic | `gcloud pubsub topics get-iam-policy TOPIC_NAME` | Grant `roles/pubsub.publisher` to `service-org-ORG_NUM@gcp-sa-scc.iam.gserviceaccount.com` |
| Finding notifications delayed | Configured filter expression too restrictive | `gcloud scc notifications describe CONFIG_NAME --organization=ORG_ID` | Verify filter: `state = "ACTIVE" AND NOT mute = "MUTED"` |

---

### Scenario 07: Cloud Asset Inventory (CAI)
| Symptom | Root Cause | Verification Command | Solution |
|---|---|---|---|
| Feed creation errors (`FAILED_PRECONDITION`) | Cloud Asset API not enabled or service agent not yet provisioned | `gcloud services list --enabled --filter="name:cloudasset.googleapis.com"` | Enable API: `gcloud services enable cloudasset.googleapis.com` |
| Asset changes missing IAM policies | `contentType` set to `RESOURCE` instead of `RESOURCE,IAM_POLICY` | `gcloud asset feeds describe FEED_NAME --organization=ORG_ID` | Update feed contentType to capture both resource definitions and IAM policy diffs |

---

### Scenario 10: Billing Account Sinks
| Symptom | Root Cause | Verification Command | Solution |
|---|---|---|---|
| Organization sink reports 100% success, but billing changes never appear | Billing Accounts exist outside the resource hierarchy | `gcloud logging sinks list --billing-account=BILLING_ID` | Deploy dedicated billing sink via `deployments/10-billing-account` |
| `PERMISSION_DENIED` creating billing sink | Deployer has Org Admin but lacks `roles/logging.configWriter` on Billing Account | `gcloud billing accounts get-iam-policy BILLING_ID` | Grant `roles/logging.configWriter` on the specific billing account ID |

---

### Scenario 11: Network Threat Detection (Cloud Armor & IDS)
| Symptom | Root Cause | Verification Command | Solution |
|---|---|---|---|
| Cloud Armor blocks traffic, but no logs appear in Cloud Logging | Logging disabled on the Backend Service | `gcloud compute backend-services list --format="table(name,logConfig.enable)"` | Run `gcloud compute backend-services update BACKEND_NAME --enable-logging --logging-sample-rate=1.0` |
| Cloud IDS threat alerts missing | Packet mirroring policy or IDS endpoint detached from VPC network | `gcloud ids endpoints list --project=PROJECT_ID` | Verify endpoint state is `READY` and packet mirroring policy is actively mirroring VPC traffic |

---

## Interactive Visual Diagnostic Tool

To open the interactive Draw.io troubleshooting decision trees directly on your desktop:

```bash
# Launch Draw.io Desktop with the interactive diagnostic decision tree
./scripts/open-diagram.sh diagrams/02-audit-logs-organization.drawio
```

Navigate to **Page 2: Troubleshooting Decision Tree** to interact with the diagnostic flowcharts and copy CLI remediation commands.
