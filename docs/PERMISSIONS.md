<picture>
  <source media="(prefers-color-scheme: dark)" srcset="../brand/abstract-logo-white.svg">
  <img alt="Abstract Security" src="../brand/abstract-logo-black.svg" width="180">
</picture>

# Permissions — every grant, at every scope

Most GCP onboarding failures are permission failures, and almost all of them are about
**scope height** rather than role name. The role is usually obvious; *where* it has to be
held is not.

Run `scripts/preflight.sh` before anything else — it checks the ones that matter.

---

## The one that blocks people

> ### `roles/logging.configWriter` at the **ORGANIZATION**
>
> This is the blocking prerequisite for an aggregated sink, and it is **rarely held by
> whoever owns the project**. Subscription Owner is not enough. Project Owner is not
> enough. Editor is not enough.
>
> It is the single most common reason a GCP onboarding session produces a decision list
> instead of a working feed. **Identify the human who holds it before scheduling
> anything.**

```bash
gcloud organizations get-iam-policy YOUR_ORG_ID \
  --flatten="bindings[].members" \
  --filter="bindings.role:roles/logging.configWriter" \
  --format="table(bindings.members)"
```

<p align="center">
  <img src="../images/diagrams/02-audit-logs-organization.png" alt="Abstract Security - GCP Org-Wide Aggregated Audit Log Pipeline" width="100%">
</p>

---

## By deployment

### `02-audit-logs-organization` / `02-audit-logs-folder` / `02-audit-logs-project`

| Principal | Role | Scope | Why |
|---|---|---|---|
| deployer | `roles/logging.configWriter` | **org / folder / project** | Create the sink. **The blocker** |
| deployer | `roles/pubsub.admin` | logging project | Topic, subscription, IAM bindings |
| deployer | `roles/iam.serviceAccountAdmin` | logging project | Create Abstract's identity |
| deployer | `roles/serviceusage.serviceUsageAdmin` | logging project | Enable APIs |
| **sink writer identity** | `roles/pubsub.publisher` | **the TOPIC** | Created *with* the sink, holds **nothing** until granted. **The #1 cause of a healthy-looking sink that delivers nothing** |
| abstract | `roles/pubsub.subscriber` | **the SUBSCRIPTION** | Abstract **pulls**. Not publisher, not project-wide |

> [!CAUTION]
> ### Deep Troubleshooting Callout: The Silent Sink Drop Failure Mode
> When Cloud Logging creates an aggregated sink, Google automatically assigns it a unique service account (`writerIdentity`), formatted as:
> `serviceAccount:service-org-ORG_NUM@gcp-sa-logging.iam.gserviceaccount.com` (or `service-PROJECT_NUM...` for project sinks).
>
> **This identity holds zero permissions by default.**
> If the `roles/pubsub.publisher` IAM grant on the destination topic is omitted or granted at the project level instead of the topic resource level:
> 1. The GCP Console displays the sink in green with "Active" status.
> 2. No error notifications are generated in the Cloud Console.
> 3. **100% of audit logs are silently dropped at write time with zero retry and zero backfill.**
>
> **Verification Command**:
> ```bash
> WRITER_SA=$(gcloud logging sinks describe abstract-org-audit-sink --organization="$ORG_ID" --format="value(writerIdentity)")
> gcloud pubsub topics get-iam-policy abstract-audit-logs --project="$LOG_PROJECT" \
>   --flatten="bindings[].members" \
>   --filter="bindings.role:roles/pubsub.publisher AND bindings.members:${WRITER_SA}" \
>   --format="table(bindings.role,bindings.members)"
> ```
> If not found, immediately execute:
> ```bash
> gcloud pubsub topics add-iam-policy-binding abstract-audit-logs --project="$LOG_PROJECT" \
>   --member="${WRITER_SA}" --role="roles/pubsub.publisher"
> ```
> See [Master Troubleshooting Guide: Step 3](TROUBLESHOOTING-GUIDE.md#step-3-sink-writer-identity--pubsub-topic-permissions-the-1-silent-failure-trap).

The writer-identity grant is automated here. It is called out because when a customer wires
this by hand, it is what they miss.

### `03-data-access`

| Principal | Role | Scope |
|---|---|---|
| deployer | **Organization Admin** (`resourcemanager.organizations.setIamPolicy`) | organization |

Not Logging Admin. Not Owner on a project. This modifies the **organization IAM policy**,
and it is usually a different person again from the `logging.configWriter` holder.

### `04-workspace`

| Principal | Role | Where | Why |
|---|---|---|---|
| deployer | `roles/iam.serviceAccountAdmin` | logging project | Create the delegated SA |
| **a human** | **Workspace SUPER ADMIN** | `admin.google.com` | Grant domain-wide delegation. **No API exists** |
| the service account | *nothing in GCP IAM* | — | Its access comes entirely from delegation |

> A GCP Owner **cannot** grant domain-wide delegation. If nobody on the call is a Workspace
> super admin, that is where the deployment stops.

### `06-scc-findings`

| Principal | Role | Scope |
|---|---|---|
| deployer | `roles/securitycenter.notificationConfigEditor` | organization |
| abstract | `roles/pubsub.subscriber` | the findings subscription |

Requires **SCC Premium or Enterprise**.

### `07-asset-inventory`

| Principal | Role | Scope | Why |
|---|---|---|---|
| deployer | `roles/cloudasset.owner` | **organization** | Create the organization feed. **Not included in Organization Admin**: without it the topic and subscription are created and the feed is refused with 403 |
| deployer | `roles/pubsub.admin` | logging project | Topic, subscription, IAM bindings |
| **Cloud Asset service agent of the logging project** (`service-<project number>@gcp-sa-cloudasset`) | `roles/pubsub.publisher` | the topic | The feed publishes as the agent of its billing project. There is no organization-level Cloud Asset agent |
| abstract | `roles/pubsub.subscriber` | the asset subscription | Read the changes |

### `09-log-archive`

| Principal | Role | Scope |
|---|---|---|
| deployer | `roles/storage.admin` | logging project |
| **archive sink writer identity** | `roles/storage.objectCreator` | the bucket |

The archive sink has its **own** writer identity, distinct from the streaming sink's. Each
sink gets one; each needs its own grant.

### `08-bucket-logs`

| Principal | Role | Scope | Why |
|---|---|---|---|
| **GCS service agent** — one PER OWNING PROJECT | `roles/pubsub.publisher` | the topic | **The notification publishes as the service agent, not as you.** Buckets in different projects have DIFFERENT agents; use `bucket_map` so each is granted, or the unlucky buckets deliver nothing |
| abstract | `roles/pubsub.subscriber` | the subscription | Read the pointer |
| abstract | `roles/storage.objectViewer` | **the bucket**, IAM-condition-scoped to `object_name_prefix` when set | Read the object the pointer points at. Without a prefix the grant is bucket-wide |
| abstract | `roles/cloudkms.cryptoKeyDecrypter` | the KMS key | CMEK buckets only — without it every fetch fails blaming Storage |

> **The notification is a pointer, not the data.** Two grants on two different services.
> Missing the second gives you notifications with no content, which reads like a parser bug
> and is not one.

### `05-health-alerts`

| Principal | Role | Scope |
|---|---|---|
| deployer | `roles/monitoring.editor` | logging project |

### `01-logging-project`

| Principal | Role | Scope |
|---|---|---|
| deployer | `roles/resourcemanager.projectCreator` | org or folder | *only* with `create_project = true` |
| deployer | `roles/billing.user` | the billing account | *only* with `create_project = true` |

---

## Least privilege, and where this repo deliberately stops short

**What is already narrow:**

- `roles/pubsub.subscriber` on **one subscription**, never project-wide
- Workspace scopes are the two `admin.reports.*.readonly` and nothing else
- Every binding is `_iam_member` (additive), never `_iam_policy` (authoritative), so nothing
  here can clobber a grant somebody else made
- `create_service_account_key` defaults **false** — a key in Terraform state is a key in
  whatever holds the state

**Where you can go narrower:**

`roles/pubsub.subscriber` grants `subscriptions.consume` but **not**
`pubsub.subscriptions.get`. Many pull clients call `GetSubscription` at startup.

`unverified:` whether Abstract's connector does. If it bites, the symptom is a **403 that
looks like a credentials problem and is not**. The hardening either way is a custom role
with `pubsub.subscriptions.consume` + `pubsub.subscriptions.get`, or adding
`roles/pubsub.viewer` on the subscription.

---

## Org policies that will block this

| Policy | Effect | Response |
|---|---|---|
| `constraints/iam.disableServiceAccountKeyCreation` | **Blocks the whole deployment** — Abstract authenticates with a service-account key | Request a scoped exception for the logging project. Longer term, Workload Identity Federation on the Abstract side is what removes the need |
| `constraints/iam.serviceAccountKeyExpiryHours` | Keys expire | Build rotation into the runbook rather than discovering it |
| `constraints/iam.disableCrossProjectServiceAccountUsage` | Blocks cross-project SA use | Keep the identity in the logging project |
| `constraints/gcp.restrictNonCmekServices` | Requires CMEK on Pub/Sub | Set the topic's KMS key |
| VPC Service Controls | Abstract pulls from **outside** the perimeter | Needs an ingress rule for the reader SA, or the logging project outside the perimeter |

The first one is the common blocker in hardened organizations, and nothing in this repo can
work around it — it is a policy exception or nothing.

---

## Key handling

The service-account key is the whole credential. Treat it accordingly:

1. **Create it out of band**, never in Terraform — `create_service_account_key` defaults
   false because a key in state is a key in whatever holds the state, and on the Cloud Shell
   path that is a home directory
2. **Upload straight to Abstract**, then `rm` the local copy
3. **Rotate on your standard cadence.** There is no automatic expiry unless the org policy
   sets one
4. **The Workspace key is broader than it looks** — domain-wide delegation is *domain*-wide
   and not project-scoped, so a leak reads the entire Workspace audit trail regardless of
   any GCP IAM control

## Quota Management & Regional Capacity

Publish quota is consumed strictly in the **destination logging project**, not in the projects generating the audit logs.

> [!TIP]
> ### Deep Troubleshooting Callout: Destination Quota Saturation
> If workloads generate massive log bursts (e.g. CI/CD runs, Dataflow jobs, or BigQuery batch queries), Pub/Sub may reject publish requests with `RESOURCE_EXHAUSTED`.
>
> 1. **Check regional publish quota utilization**:
>    ```bash
>    gcloud monitoring metrics list \
>      --project="$LOG_PROJECT" \
>      --filter="metric.type:pubsub.googleapis.com/topic/byte_publish_utilization"
>    ```
> 2. **Remediation**:
>    - Separate noisy workloads (`11-network-threats`) into dedicated topics and logging projects.
>    - Request a Pub/Sub quota increase via Google Cloud Support for `pubsub.googleapis.com/regional_publish_throughput`.
>    - Deploy `05-health-alerts` to receive automated alerts before messages are dropped.

---

## Checking all of this

```bash
./scripts/preflight.sh --project YOUR_LOG_PROJECT --org-id YOUR_ORG_ID --report ~/readiness.md
```

Read-only. It checks identity, APIs, the `logging.configWriter` grant at your chosen scope,
whether Data Access is already enabled, and whether sinks already exist — then writes a
report with a numbered action list.

---

## Related Documentation & Visual Models

* 📘 **Telemetry Dataflow Reference**: [Master GCP Telemetry Dataflow Reference](DATAFLOW-AND-ARCHITECTURE-REFERENCE.md)
* 🛠️ **Diagnostic Runbook**: [Master Troubleshooting Guide](TROUBLESHOOTING-GUIDE.md)
* 🌐 **Interactive Diagram Explorer**: [Architecture Explorer Web Viewer](architecture-explorer.html)
* 🎨 **Interactive Draw.io Launcher**: `./scripts/open-diagram.sh 02-audit-logs-organization`
