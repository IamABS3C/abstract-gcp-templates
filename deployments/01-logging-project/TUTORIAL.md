<img src="../../brand/abstract-logo-white.svg" alt="Abstract Security" width="150">

# Bootstrap the logging project

<!-- guided-step -->
> **This is step 3 of the guided setup (Logging project).** The guided setup does it for you and checks it: from the repository root run `./scripts/abstract-gcp-setup.sh --step 3`, or follow `WALKTHROUGH.md`. This page is the Terraform way to do the same step.
<!-- /guided-step -->

<walkthrough-tutorial-duration duration="10"></walkthrough-tutorial-duration>

**Optional.** Most customers already have a security or logging project — point
`02-audit-logs-organization` at it and skip this.

Run this for greenfield, or when the only candidate is a **workload** project. That is the
wrong answer: Pub/Sub publish quota is consumed in the destination project, and a security
pipeline inside a workload project can be read or broken by that workload's owner.

## Sign in first

Cloud Shell opened this repository in a **temporary** session: Google gives repositories it does not own none of your credentials, and deletes the session's files when it ends.

Sign in, then give Terraform the same sign-in:

```bash
gcloud auth login
gcloud auth application-default login
```

<walkthrough-info-message>**Keep the Terraform state outside this session.** Copy `backend.tf.example` to `backend.tf` and set its bucket before `terraform apply`, or the state is deleted when the session ends.</walkthrough-info-message>

## Enable APIs on an existing project

```bash
cat > terraform.tfvars <<EOF
project_id = "YOUR_EXISTING_PROJECT"
EOF
terraform init && terraform apply
```

## Or create the project too

```bash
cat > terraform.tfvars <<EOF
create_project     = true
project_id         = "acme-security-logging"
org_id             = "YOUR_ORG_ID"
billing_account_id = "XXXXXX-XXXXXX-XXXXXX"
EOF
```

Needs project-creator rights and a billing account — a project with no billing account
cannot publish to Pub/Sub.

`deletion_policy` defaults to **PREVENT**, which is right for a project holding an audit
pipeline.

## Step 3 — Verify the deployment

Run these verification commands before proceeding to ensure the logging project is ready for telemetry:

```bash
# 1. Confirm the project was provisioned and active
PROJ=$(terraform output -raw project_id)
echo "Logging project: $PROJ"

# 2. Verify that Pub/Sub and Logging APIs are enabled
gcloud services list --project="$PROJ" --enabled \
  --filter="name:(pubsub.googleapis.com OR logging.googleapis.com OR iam.googleapis.com)"

# 3. Verify billing is linked (required for Pub/Sub quotas)
gcloud beta billing projects describe "$PROJ" --format="table(billingAccountName,billingEnabled)"
```

### Failure Troubleshooting Tips

* **Error: `billingAccount not configured` or `FAILED_PRECONDITION`**:
  Pub/Sub cannot create topics without active billing. Re-link your billing account:
  ```bash
  gcloud beta billing projects link "$PROJ" --billing-account="YOUR_BILLING_ACCOUNT_ID"
  ```
* **Error: `The caller does not have permission` during project creation**:
  Your identity needs `roles/resourcemanager.projectCreator` on the Organization or parent Folder:
  ```bash
  gcloud organizations add-iam-policy-binding "YOUR_ORG_ID" \
    --member="user:$(gcloud config get-value account)" \
    --role="roles/resourcemanager.projectCreator"
  ```
* **Error: `API is not enabled`**:
  Enable missing APIs manually:
  ```bash
  gcloud services enable pubsub.googleapis.com logging.googleapis.com iam.googleapis.com --project="$PROJ"
  ```

<walkthrough-conclusion-trophy></walkthrough-conclusion-trophy>

```bash
terraform output preflight
```

That names the grants Terraform cannot verify for you — including
`roles/logging.configWriter` at the organization, the one that actually blocks people.

---

<sub>**Abstract Security · GCP log export** — [all scenarios](../../README.md) · [architecture](../../docs/ARCHITECTURE.md) · [permissions](../../docs/PERMISSIONS.md) · [filters](../../docs/FILTERS.md)</sub>

