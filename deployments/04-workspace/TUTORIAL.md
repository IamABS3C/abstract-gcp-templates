<img src="../../brand/abstract-logo-white.svg" alt="Abstract Security" width="150">

# Google Workspace identity logs

<!-- guided-step -->
> **This is step 7 of the guided setup (Google Workspace logs).** The guided setup does it for you and checks it: from the repository root run `./scripts/abstract-gcp-setup.sh --step 7`, or follow `WALKTHROUGH.md`. This page is the Terraform way to do the same step.
<!-- /guided-step -->

<walkthrough-tutorial-duration duration="15"></walkthrough-tutorial-duration>

A **separate pipeline**. Workspace audit data comes from the Admin SDK Reports API and never
touches Cloud Logging — no sink, topic or filter at any scope will collect it.

<walkthrough-info-message>You need a Workspace **SUPER ADMIN** for step 3. A Google Cloud
Owner cannot grant domain-wide delegation — there is no API for it and no Terraform
provider.</walkthrough-info-message>

## Sign in first

Cloud Shell opened this repository in a **temporary** session: Google gives repositories it does not own none of your credentials, and deletes the session's files when it ends.

Sign in, then give Terraform the same sign-in:

```bash
gcloud auth login
gcloud auth application-default login
```

<walkthrough-info-message>**Keep the Terraform state outside this session.** Copy `backend.tf.example` to `backend.tf` and set its bucket before `terraform apply`, or the state is deleted when the session ends.</walkthrough-info-message>

## Step 1 — Plan and apply

```bash
cat > terraform.tfvars <<EOF
log_project           = "YOUR_PROJECT"
workspace_admin_email = "admin@yourdomain.com"
workspace_app_groups  = ["identity", "admin"]
EOF
terraform init && terraform apply
```

`identity` is `login`, `saml`, `token`, `user_accounts`, `context_aware_access` — the answer
to "who signed in", which is usually the whole ask. Add `data` for gmail and drive only
after measuring; they dwarf everything else.

## Step 2 — Read the values you need

```bash
terraform output workspace_onboarding
```

## Step 3 — Grant delegation (Workspace super admin)

**admin.google.com → Security → Access and data control → API controls →
Domain-wide delegation → Add new**

Paste the `client_id` — the **numeric** ID, not the service-account email — and the two
scopes exactly as printed, comma-separated with no spaces.

## Step 4 — Key, then Abstract

```bash
SA=$(terraform output -json workspace_onboarding | jq -r .service_account_email)
echo "Service Account: $SA"
mkdir -p ~/abstract-keys && chmod 700 ~/abstract-keys   # outside the repo clone
gcloud iam service-accounts keys create ~/abstract-keys/abstract-workspace-key.json --iam-account="$SA" --project="YOUR_PROJECT"
chmod 600 ~/abstract-keys/abstract-workspace-key.json
```

`-json | jq` rather than `-raw`: **`-raw` only works on a string output and errors on an
object**, which `workspace_onboarding` is.

Upload it to Abstract with the admin email and application list, then **delete the local
copy**:
```bash
rm ~/abstract-keys/abstract-workspace-key.json
```

## Step 5 — Verification & Failure Troubleshooting

Run these checks to confirm the service account and APIs are properly configured:

```bash
# 1. Confirm Admin SDK API is enabled in your logging project
gcloud services list --project="YOUR_PROJECT" --enabled --filter="name:admin.googleapis.com"

# 2. Inspect the exact numeric Client ID and scopes required for Workspace DWD
terraform output -json workspace_onboarding | jq -r '{client_id: .client_id, scopes: .scopes}'

# 3. Test service account status in Google Cloud
gcloud iam service-accounts describe "$SA" --project="YOUR_PROJECT" \
  --format="table(email,disabled)"
```

### Failure Troubleshooting Tips

* **Failure: HTTP 401 Unauthorized (`Invalid impersonation prn email address`)**:
  Domain-wide delegation impersonates the subject passed in `workspace_admin_email`. If that user does not exist or is not a Workspace Admin, all API queries fail with 401. Ensure the user is an active Workspace administrator.
* **Failure: HTTP 403 Forbidden (`Client not authorized for requested scopes`)**:
  In `admin.google.com ➔ Security ➔ Access and data control ➔ API controls ➔ Domain-wide delegation`, check that:
  1. The **numeric Client ID** was entered, NOT the service account email.
  2. The scopes list contains commas with **zero spaces**.
* **Failure: DWD Propagation Delay**:
  After granting Domain-Wide Delegation in Workspace, allow **5 to 10 minutes** for Google identity caches to synchronize before testing in Abstract.

<walkthrough-conclusion-trophy></walkthrough-conclusion-trophy>

If you only need real-time user sign-in events and have Super Admin access, remember that
**Pathway A (Native Cloud Audit Logs Sharing)** streams Workspace logins directly into
`02-audit-logs-organization` with zero DWD service account keys.


---

<sub>**Abstract Security · GCP log export** — [all scenarios](../../README.md) · [architecture](../../docs/ARCHITECTURE.md) · [permissions](../../docs/PERMISSIONS.md) · [filters](../../docs/FILTERS.md)</sub>
