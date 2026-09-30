<img src="../../brand/abstract-logo-white.svg" alt="Abstract Security" width="150">

# Single-project pilot

<!-- guided-step -->
> **This is step 4 of the guided setup (Log pipeline).** The guided setup does it for you and checks it: from the repository root run `./scripts/abstract-gcp-setup.sh --step 4`, or follow `WALKTHROUGH.md`. This page is the Terraform way to do the same step.
<!-- /guided-step -->

<walkthrough-tutorial-duration duration="10"></walkthrough-tutorial-duration>

<walkthrough-info-message>**This does not cover future projects.** A project sink has no
`include_children`, because nothing exists below a project. This is a pilot — it proves the
whole pipeline end to end before you ask for organization-scope IAM, which is usually the
real blocker.</walkthrough-info-message>

Choosing this directory *is* the acknowledgement — the module normally refuses project
scope without one.

## Step 1 — Preflight

```bash
../../scripts/preflight.sh --project YOUR_PROJECT --scope project
```

## Step 2 — Plan, then apply

```bash
cat > terraform.tfvars <<EOF
log_project  = "YOUR_PROJECT"
sink_project = "YOUR_PROJECT"
EOF
terraform init && terraform plan
```

## Step 3 — Then replace it

<walkthrough-conclusion-trophy></walkthrough-conclusion-trophy>

Once you have proven the pipeline and obtained `roles/logging.configWriter` at the
organization, deploy `02-audit-logs-organization` and **delete this sink**.

**Do not repeat this per project.** Seventy project sinks is exactly the linear toil the
aggregated sink exists to eliminate — and each one silently decays as projects change.

---

<sub>**Abstract Security · GCP log export** — [all scenarios](../../README.md) · [architecture](../../docs/ARCHITECTURE.md) · [permissions](../../docs/PERMISSIONS.md) · [filters](../../docs/FILTERS.md)</sub>
