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
echo "$SA"
gcloud iam service-accounts keys create ws-key.json --iam-account="$SA"
```

`-json | jq` rather than `-raw`: **`-raw` only works on a string output and errors on an
object**, which `workspace_onboarding` is.

Upload it to Abstract with the admin email and application list, then **delete the local
copy**.

<walkthrough-conclusion-trophy></walkthrough-conclusion-trophy>

If the Reports API returns **401**, the delegation has not propagated or `admin_email` is
not actually an admin. Delegation impersonates a real user — without a valid subject you
get 401, not an empty result.

---

<sub>**Abstract Security · GCP log export** — [all scenarios](../../README.md) · [architecture](../../docs/ARCHITECTURE.md) · [permissions](../../docs/PERMISSIONS.md) · [filters](../../docs/FILTERS.md)</sub>
