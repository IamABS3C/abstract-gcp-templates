#!/usr/bin/env bash
# Every guard in this repo must actually reject what its message claims.
#
# A guard that does not fire is worse than no guard: it reads as a control in
# review and does nothing at runtime. Each case below asserts the REJECTION,
# and each block ends with a POSITIVE control asserting the valid case passes —
# because a guard that rejects everything is equally useless.
set -uo pipefail
cd "$(dirname "$0")/.." || exit 1
pass=0; fail=0

check() { # name  dir  tfvars  expected-substring
  local name="$1" dir="$2" vars="$3" want="$4"
  printf '%s\n' "$vars" > /tmp/g.tfvars
  local out
  out=$( cd "$dir" && tofu init -backend=false -no-color >/dev/null 2>&1
         tofu plan -no-color -var-file=/tmp/g.tfvars -input=false 2>&1 )
  if [[ "$want" == "PASS" ]]; then
    if grep -q "precondition failed" <<<"$out"; then
      printf "  FAIL  %-46s (expected to pass, guard fired)\n" "$name"; fail=$((fail+1))
    else printf "  ok    %-46s\n" "$name"; pass=$((pass+1)); fi
  else
    if grep -qF "$want" <<<"$out"; then
      printf "  ok    %-46s\n" "$name"; pass=$((pass+1))
    else printf "  FAIL  %-46s (guard did NOT fire)\n" "$name"; fail=$((fail+1)); fi
  fi
}

echo "log-export"
check "unknown log category rejected"      modules/log-export 'org_id="1"
log_project="p"
log_categories=["admin_activity","firewal"]' "Unknown log_categories"
check "extreme tier needs acknowledgement" modules/log-export 'org_id="1"
log_project="p"
log_categories=["vpc_flows"]' "dominate your entire bill"
check "project scope needs acknowledgement" modules/log-export 'org_id="1"
log_project="p"
sink_scope="project"' "defeats the point"
check "folder scope needs folder_id"       modules/log-export 'org_id="1"
log_project="p"
sink_scope="folder"' "requires folder_id"
check "push endpoint needs OIDC"           modules/log-export 'org_id="1"
log_project="p"
push_endpoint="https://x.example/i"' "requires push_service_account_email"
check "default config passes"              modules/log-export 'org_id="1"
log_project="p"' PASS

echo "audit-config"
check "allServices needs acknowledgement"  modules/audit-config 'scope="organization"
org_id="1"' "THIS APPLY REMOVES THEM"
check "ADMIN_WRITE rejected"               modules/audit-config 'scope="organization"
org_id="1"
services=["bigquery.googleapis.com"]
log_types=["ADMIN_WRITE"]' "always on, cannot be disabled"
check "named services pass"                modules/audit-config 'scope="organization"
org_id="1"
services=["bigquery.googleapis.com"]' PASS

echo "workspace"
check "needs admin email"                  modules/workspace 'enable_workspace=true
log_project="p"' "requires workspace_admin_email"
check "gmail/drive need acknowledgement"   modules/workspace 'enable_workspace=true
log_project="p"
workspace_admin_email="a@b.com"
workspace_app_groups=["data"]' "volume monsters"
check "identity+admin passes"              modules/workspace 'enable_workspace=true
log_project="p"
workspace_admin_email="a@b.com"' PASS

echo "gcs-notifications"
check "empty bucket list rejected"         modules/gcs-notifications 'buckets=[]
bucket_project="p"
log_project="p"' "no org-level equivalent"
check "OBJECT_DELETE needs acknowledgement" modules/gcs-notifications 'buckets=["b"]
bucket_project="p"
log_project="p"
event_types=["OBJECT_FINALIZE","OBJECT_DELETE"]' "no longer exist"
check "single bucket passes"               modules/gcs-notifications 'buckets=["b"]
bucket_project="p"
log_project="p"' PASS
check "bucket_map across projects passes"  modules/gcs-notifications 'bucket_map={"b1"="proj-a","b2"="proj-b"}
log_project="p"' PASS

echo "monitoring"
check "no channel needs acknowledgement"   modules/monitoring 'log_project="p"
subscription_id="s"
topic_id="t"' "fire into the void"
check "threshold beyond retention rejected" modules/monitoring 'log_project="p"
subscription_id="s"
topic_id="t"
notification_channels=["c"]
unacked_age_threshold_seconds=999999' "already lost"
check "sane thresholds pass"               modules/monitoring 'log_project="p"
subscription_id="s"
topic_id="t"
notification_channels=["c"]' PASS

echo "asset-inventory"
check "needs a subscriber identity"        modules/asset-inventory 'org_id="1"
log_project="p"' "subscriber_service_account_email is required"
check "empty asset_types needs ack"        modules/asset-inventory 'org_id="1"
log_project="p"
subscriber_service_account_email="a@b.com"
asset_types=[]' "feeds EVERY asset type"
check "bad content_type rejected"          modules/asset-inventory 'org_id="1"
log_project="p"
subscriber_service_account_email="a@b.com"
content_type="NONSENSE"' "content_type must be one of"
check "defaults pass"                      modules/asset-inventory 'org_id="1"
log_project="p"
subscriber_service_account_email="a@b.com"' PASS

echo "archive"
check "archive needs a bucket name"        modules/archive 'enable_gcs_archive=true
log_project="p"
org_id="1"
filter="x"' "requires archive_bucket_name"

printf "\n  %d passed, %d failed\n" "$pass" "$fail"
[[ "$fail" -gt 0 ]] && exit 1 || exit 0
