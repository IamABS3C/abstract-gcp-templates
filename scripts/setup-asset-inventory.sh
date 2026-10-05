#!/usr/bin/env bash
# =============================================================================
#   Abstract Security — Standalone Cloud Asset Inventory Feeds Setup
# =============================================================================
set -euo pipefail

# shellcheck disable=SC2034  # the full palette is defined in every setup script
B=$'\033[1m' P=$'\033[38;5;198m' G=$'\033[0;32m' Y=$'\033[0;33m' R=$'\033[0;31m' C=$'\033[0;36m' D=$'\033[2m' O=$'\033[0m'
# Fail loudly: any gcloud call that fails stops the script with a non-zero exit, so it can
# never print "complete" over a half-built pipeline.
die() { printf '%s✗ %s%s\n' "$R" "$*" "$O" >&2; exit 1; }
trap 'printf "%s✗ a command failed at line %s; nothing after it ran%s\n" "$R" "$LINENO" "$O" >&2' ERR
banner() {
  printf "%s" "$P"
  cat <<'EOF'
    _   _         _                  _     ___                      _ _         
   /_\ | |__  ___| |_ _ _ __ _  __ _| |_  / __| ___ __ _  _ _ _(_) |_ _  _ 
  / _ \| '_ \(_-<  _| '_/ _` |/ _` |  _| \__ \/ -_) _| || | '_| |  _| || |
 /_/ \_\_.__/__/\__|_| \__,_|\__, |\__| |___/\___\__|\_,_|_| |_|\__|\_, |
                              |___/                                   |__/ 
EOF
  printf "%s" "$O"
  printf "%s   Standalone Cloud Asset Inventory Real-Time Feeds Setup%s\n\n" "$D" "$O"
}

banner

ORG_ID="${1:-}"
LOG_PROJECT="${2:-}"

if [[ -z "$ORG_ID" ]]; then
  DISCOVERED_ORG=$(gcloud organizations list --format="value(ID)" 2>/dev/null | head -n1 || true)
  read -r -p "  Enter Organization ID [${DISCOVERED_ORG}]: " input_org </dev/tty
  ORG_ID="${input_org:-$DISCOVERED_ORG}"
fi

if [[ -z "$LOG_PROJECT" ]]; then
  CURRENT_PROJ=$(gcloud config get-value project 2>/dev/null || true)
  read -r -p "  Enter Logging Project ID [${CURRENT_PROJ}]: " input_proj </dev/tty
  LOG_PROJECT="${input_proj:-$CURRENT_PROJ}"
fi

[[ -z "$ORG_ID" || -z "$LOG_PROJECT" ]] && { echo "Organization ID and Logging Project ID are required."; exit 1; }

TOPIC_NAME="abstract-asset-inventory"
SUB_NAME="abstract-asset-inventory-sub"
FEED_ID="abstract-asset-feed"
SA_NAME="abstract-asset-reader"
KEY_DIR="$HOME/abstract-keys"
mkdir -p "$KEY_DIR" && chmod 700 "$KEY_DIR"
KEY_FILE="$KEY_DIR/abstract-asset-key.json"

echo "Enabling cloudasset.googleapis.com on $LOG_PROJECT..."
gcloud services enable cloudasset.googleapis.com --project="$LOG_PROJECT" \
  || die "could not enable cloudasset.googleapis.com on $LOG_PROJECT"

echo "Creating Pub/Sub Topic and Subscription in $LOG_PROJECT..."
gcloud pubsub topics describe "$TOPIC_NAME" --project="$LOG_PROJECT" >/dev/null 2>&1 \
  || gcloud pubsub topics create "$TOPIC_NAME" --project="$LOG_PROJECT" \
  || die "could not create topic $TOPIC_NAME in $LOG_PROJECT"
gcloud pubsub subscriptions describe "$SUB_NAME" --project="$LOG_PROJECT" >/dev/null 2>&1 \
  || gcloud pubsub subscriptions create "$SUB_NAME" --topic="$TOPIC_NAME" --project="$LOG_PROJECT" \
       --ack-deadline=60 --message-retention-duration=7d --expiration-period=never \
  || die "could not create subscription $SUB_NAME in $LOG_PROJECT"

PROJECT_NUM=$(gcloud projects describe "$LOG_PROJECT" --format="value(projectNumber)") \
  || die "could not read the project number of $LOG_PROJECT"
[[ -n "$PROJECT_NUM" ]] || die "empty project number for $LOG_PROJECT"
ASSET_AGENT="serviceAccount:service-$PROJECT_NUM@gcp-sa-cloudasset.iam.gserviceaccount.com"

echo "Granting roles/pubsub.publisher to Cloud Asset Service Agent ($ASSET_AGENT)..."
gcloud pubsub topics add-iam-policy-binding "$TOPIC_NAME" --project="$LOG_PROJECT" \
  --member="$ASSET_AGENT" --role="roles/pubsub.publisher" >/dev/null \
  || die "could not grant roles/pubsub.publisher on $TOPIC_NAME to $ASSET_AGENT"

TOPIC_URI="//pubsub.googleapis.com/projects/$LOG_PROJECT/topics/$TOPIC_NAME"

echo "Creating Cloud Asset Organization Feed ($FEED_ID)..."
gcloud asset feeds describe "$FEED_ID" --organization="$ORG_ID" >/dev/null 2>&1 \
  || gcloud asset feeds create "$FEED_ID" \
       --organization="$ORG_ID" \
       --pubsub-topic="$TOPIC_URI" \
       --content-type=resource \
       --asset-types="compute.googleapis.com/Firewall,iam.googleapis.com/Role,iam.googleapis.com/ServiceAccount,storage.googleapis.com/Bucket" \
  || die "could not create asset feed $FEED_ID (needs roles/cloudasset.owner on organization $ORG_ID)"

echo "Creating Subscriber Service Account ($SA_NAME)..."
SA_EMAIL="$SA_NAME@$LOG_PROJECT.iam.gserviceaccount.com"
gcloud iam service-accounts describe "$SA_EMAIL" --project="$LOG_PROJECT" >/dev/null 2>&1 \
  || gcloud iam service-accounts create "$SA_NAME" --project="$LOG_PROJECT" --display-name="Abstract Asset Inventory Reader" \
  || die "could not create service account $SA_NAME in $LOG_PROJECT"

gcloud pubsub subscriptions add-iam-policy-binding "$SUB_NAME" --project="$LOG_PROJECT" \
  --member="serviceAccount:$SA_EMAIL" --role="roles/pubsub.subscriber" >/dev/null \
  || die "could not grant roles/pubsub.subscriber on $SUB_NAME to $SA_EMAIL"

if [[ ! -f "$KEY_FILE" ]]; then
  gcloud iam service-accounts keys create "$KEY_FILE" --iam-account="$SA_EMAIL" --project="$LOG_PROJECT" \
    || die "could not create a key for $SA_EMAIL"
  chmod 600 "$KEY_FILE"
fi

printf "\n%s✓ Cloud Asset Inventory Setup complete!%s\n" "$G" "$O"
printf "  • Subscription:    %s%s%s\n" "$B" "$SUB_NAME" "$O"
printf "  • Credentials:     %s%s%s\n" "$B" "$KEY_FILE" "$O"
printf "  • Abstract Parser: %sparsers/cloud-asset-inventory.yml%s (only on the configuration for %s, never on the audit-log one)\n\n" "$C" "$O" "$SUB_NAME"
