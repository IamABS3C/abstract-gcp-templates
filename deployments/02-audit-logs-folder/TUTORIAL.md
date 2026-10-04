<img src="../../brand/abstract-logo-white.svg" alt="Abstract Security" width="150">

# Folder-scope log export

<!-- guided-step -->
> **This is step 4 of the guided setup (Log pipeline).** The guided setup does it for you and checks it: from the repository root run `./scripts/abstract-gcp-setup.sh --step 4`, or follow `WALKTHROUGH.md`. This page is the Terraform way to do the same step.
<!-- /guided-step -->

<walkthrough-tutorial-duration duration="10"></walkthrough-tutorial-duration>

Same containment guarantee as organization scope, one ring in: **every project in this
folder and every sub-folder, current and future.**

Use this when org-scope IAM has not been granted yet — and note what it costs you: any
project *outside* this folder is silently missed. That is a real gap, not a rounding error.

## Sign in first

Cloud Shell opened this repository in a **temporary** session: Google gives repositories it does not own none of your credentials, and deletes the session's files when it ends.

Sign in, then give Terraform the same sign-in:

```bash
gcloud auth login
gcloud auth application-default login
```

<walkthrough-info-message>**Keep the Terraform state outside this session.** Copy `backend.tf.example` to `backend.tf` and set its bucket before `terraform apply`, or the state is deleted when the session ends.</walkthrough-info-message>

## Step 1 — Find the folder

```bash
gcloud resource-manager folders list --organization=YOUR_ORG_ID
```

## Step 2 — Preflight

```bash
../../scripts/preflight.sh --project YOUR_LOG_PROJECT --folder-id YOUR_FOLDER_ID
```

You need `roles/logging.configWriter` **at the folder**.

## Step 3 — Plan, then apply

```bash
cat > terraform.tfvars <<EOF
folder_id   = "YOUR_FOLDER_ID"
log_project = "YOUR_LOG_PROJECT"
EOF
terraform init && terraform plan && terraform apply
```

Read `effective_filter` and `volume_profile` before applying:
```bash
terraform output -raw effective_filter
terraform output volume_profile
terraform output abstract_onboarding
```

## Step 4 — Verification & Failure Troubleshooting

Run these checks to ensure the folder sink is operational:

```bash
# 1. Verify folder sink exists and includes child containers
gcloud logging sinks describe abstract-folder-sink --folder="YOUR_FOLDER_ID" \
  --format="table(name,destination,includeChildren)"

# 2. Verify sink writer identity is authorized on the Pub/Sub topic
WRITER=$(terraform output -raw sink_writer_identity)
echo "Writer identity: $WRITER"
gcloud pubsub topics get-iam-policy abstract-audit-logs --project="YOUR_LOG_PROJECT"

# 3. Pull verification event from Pub/Sub
gcloud pubsub subscriptions pull abstract-audit-logs-sub \
  --project="YOUR_LOG_PROJECT" --limit=3 --auto-ack
```

### Failure Troubleshooting Tips

* **Failure: Missing logs from child projects**:
  Ensure `--include-children` is active on the folder sink:
  ```bash
  gcloud logging sinks update abstract-folder-sink --folder="YOUR_FOLDER_ID" --include-children
  ```
* **Failure: Silent Drop (#1 Trap)**:
  If writer identity lacks `roles/pubsub.publisher` on the destination topic:
  ```bash
  gcloud pubsub topics add-iam-policy-binding abstract-audit-logs \
    --project="YOUR_LOG_PROJECT" \
    --member="$WRITER" \
    --role="roles/pubsub.publisher"
  ```
* **Failure: Permission Denied during apply**:
  Ensure you hold `roles/logging.configWriter` on the folder:
  ```bash
  gcloud resource-manager folders add-iam-policy-binding "YOUR_FOLDER_ID" \
    --member="user:$(gcloud config get-value account)" \
    --role="roles/logging.configWriter"
  ```

<walkthrough-conclusion-trophy></walkthrough-conclusion-trophy>

**When org scope becomes available, move to `02-audit-logs-organization`** rather than adding more
folder sinks. Several folder sinks is the shape this design exists to avoid.

---

<sub>**Abstract Security · GCP log export** — [all scenarios](../../README.md) · [architecture](../../docs/ARCHITECTURE.md) · [permissions](../../docs/PERMISSIONS.md) · [filters](../../docs/FILTERS.md)</sub>

