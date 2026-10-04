<img src="../../brand/abstract-logo-white.svg" alt="Abstract Security" width="150">

# Security Command Center findings

<walkthrough-tutorial-duration duration="10"></walkthrough-tutorial-duration>

<walkthrough-info-message>**SCC does not flow through the Log Router.** It publishes to
Pub/Sub through its own NotificationConfig. No sink filter, at any scope, will ever collect
it — which is why this is a separate deployment rather than a checkbox on the log
export.</walkthrough-info-message>

Needs **SCC Premium or Enterprise**, and
`roles/securitycenter.notificationConfigEditor` at the organization.

## Sign in first

Cloud Shell opened this repository in a **temporary** session: Google gives repositories it does not own none of your credentials, and deletes the session's files when it ends.

Sign in, then give Terraform the same sign-in:

```bash
gcloud auth login
gcloud auth application-default login
```

<walkthrough-info-message>**Keep the Terraform state outside this session.** Copy `backend.tf.example` to `backend.tf` and set its bucket before `terraform apply`, or the state is deleted when the session ends.</walkthrough-info-message>

## Step 1 — Reuse Abstract's existing identity

If you already deployed `02-audit-logs-organization`, take the service-account email from its output
rather than making a second identity to rotate:

```bash
cd ../02-audit-logs-organization
terraform output -json abstract_onboarding | jq -r .service_account_email
cd ../06-scc-findings
```

`-json | jq`, not `-raw`: **`-raw` errors on an object output.**

Better still, skip the copy entirely — set `remote_state_bucket` and it is read from
`02-audit-logs-organization`'s state:

```hcl
remote_state_bucket = "acme-abstract-tfstate"
remote_state_prefix = "01-organization"  # its state key keeps the original folder name
```

<walkthrough-info-message>**Prerequisite Preflight Check:** Verify your organization has SCC enabled and can query findings before provisioning notification feeds:</walkthrough-info-message>

```bash
# Verify SCC API access and active findings
gcloud scc findings list --organization="YOUR_ORG_ID" --limit=1
```

If this command returns `PERMISSION_DENIED`, obtain `roles/securitycenter.admin` or `roles/securitycenter.notificationConfigEditor` before proceeding.

## Step 2 — Decide the filter

The default is **active, unmuted** findings:

```
state="ACTIVE" AND NOT mute="MUTED"
```

On a mature SCC deployment muted and resolved findings are the bulk of the volume and
none of the signal. Widen this deliberately, not by default.

## Step 3 — Plan, then apply

```bash
cat > terraform.tfvars <<EOF
org_id                           = "YOUR_ORG_ID"
log_project                      = "YOUR_LOG_PROJECT"
subscriber_service_account_email = "abstract-pubsub-reader@YOUR_LOG_PROJECT.iam.gserviceaccount.com"
filter                           = "state=\"ACTIVE\" AND NOT mute=\"MUTED\""
EOF
terraform init && terraform plan
```

When the plan verifies, apply:

```bash
terraform apply
```

## Step 4 — Verify the deployment and outputs

Check that the resources were provisioned:

```bash
terraform output -raw scc_topic
terraform output -raw scc_subscription
```

Inspect the notification config at the organization:

```bash
gcloud scc notifications describe abstract-scc-findings-config --organization=YOUR_ORG_ID
```

Confirm the subscription exists and can receive findings:

```bash
gcloud pubsub subscriptions describe abstract-scc-findings-sub --project=YOUR_LOG_PROJECT
```

## Step 5 — Troubleshooting & Failure Modes

Before wrapping up, verify the two most common failure modes:

### 1. The SCC Service Agent Publisher Role Trap
SCC publishes using its organization service agent, formatted as `service-org-ORG_NUM@gcp-sa-scc-notification.iam.gserviceaccount.com`. If this identity loses `roles/pubsub.publisher`, findings are dropped silently:

```bash
gcloud pubsub topics get-iam-policy abstract-scc-findings \
  --project=YOUR_LOG_PROJECT \
  --filter="bindings.role:roles/pubsub.publisher"
```

### 2. Muted Findings Not Appearing
If you trigger a test finding in SCC and it does not arrive on Pub/Sub:
1. Check if the finding was auto-muted by an SCC mute rule:
   ```bash
   gcloud scc findings list --organization=YOUR_ORG_ID --filter="mute=\"MUTED\"" --limit=5
   ```
2. Muted findings are explicitly excluded by `NOT mute="MUTED"`. To test unmuted flow, unmute the finding in the SCC console or adjust your filter.

<walkthrough-conclusion-trophy></walkthrough-conclusion-trophy>

Findings arrive on their **own** topic and subscription. They are a different shape from
audit logs, so configure them as a separate source in Abstract rather than expecting the
audit-log parser to handle them.

---

<sub>**Abstract Security · GCP log export** — [all scenarios](../../README.md) · [architecture](../../docs/ARCHITECTURE.md) · [permissions](../../docs/PERMISSIONS.md) · [filters](../../docs/FILTERS.md)</sub>
