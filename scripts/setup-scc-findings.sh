#!/usr/bin/env bash
# =============================================================================
#   Abstract Security — Standalone Security Command Center (SCC) Findings Setup
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
  printf "%s   Standalone Security Command Center (SCC) Telemetry Setup%s\n\n" "$D" "$O"
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

TOPIC_NAME="abstract-scc-findings"
SUB_NAME="abstract-scc-findings-sub"
NOTIF_ID="abstract-scc-notifications"
SA_NAME="abstract-scc-reader"
KEY_DIR="$HOME/abstract-keys"
mkdir -p "$KEY_DIR" && chmod 700 "$KEY_DIR"
KEY_FILE="$KEY_DIR/abstract-scc-key.json"

echo "Creating Pub/Sub Topic and Subscription in $LOG_PROJECT..."
gcloud pubsub topics describe "$TOPIC_NAME" --project="$LOG_PROJECT" >/dev/null 2>&1 \
  || gcloud pubsub topics create "$TOPIC_NAME" --project="$LOG_PROJECT" \
  || die "could not create topic $TOPIC_NAME in $LOG_PROJECT"
gcloud pubsub subscriptions describe "$SUB_NAME" --project="$LOG_PROJECT" >/dev/null 2>&1 \
  || gcloud pubsub subscriptions create "$SUB_NAME" --topic="$TOPIC_NAME" --project="$LOG_PROJECT" \
       --ack-deadline=60 --message-retention-duration=7d --expiration-period=never \
  || die "could not create subscription $SUB_NAME in $LOG_PROJECT"

TOPIC_URI="projects/$LOG_PROJECT/topics/$TOPIC_NAME"
SCC_AGENT="serviceAccount:service-org-$ORG_ID@gcp-sa-scc-notification.iam.gserviceaccount.com"

echo "Granting roles/pubsub.publisher on topic to SCC Service Agent ($SCC_AGENT)..."
gcloud pubsub topics add-iam-policy-binding "$TOPIC_NAME" --project="$LOG_PROJECT" \
  --member="$SCC_AGENT" --role="roles/pubsub.publisher" >/dev/null \
  || die "could not grant roles/pubsub.publisher on $TOPIC_NAME to $SCC_AGENT"

echo "Configuring SCC Organization NotificationConfig ($NOTIF_ID)..."
gcloud scc notifications create "$NOTIF_ID" \
  --organization="$ORG_ID" \
  --pubsub-topic="$TOPIC_URI" \
  --description="Abstract Security real-time finding notifications" \
  --filter="state=\"ACTIVE\"" 2>/dev/null || \
gcloud scc notifications update "$NOTIF_ID" \
  --organization="$ORG_ID" \
  --pubsub-topic="$TOPIC_URI" \
  || die "could not create or update SCC notification $NOTIF_ID"

echo "Creating Subscriber Service Account ($SA_NAME)..."
SA_EMAIL="$SA_NAME@$LOG_PROJECT.iam.gserviceaccount.com"
gcloud iam service-accounts describe "$SA_EMAIL" --project="$LOG_PROJECT" >/dev/null 2>&1 \
  || gcloud iam service-accounts create "$SA_NAME" --project="$LOG_PROJECT" --display-name="Abstract SCC Reader" \
  || die "could not create service account $SA_NAME in $LOG_PROJECT"

gcloud pubsub subscriptions add-iam-policy-binding "$SUB_NAME" --project="$LOG_PROJECT" \
  --member="serviceAccount:$SA_EMAIL" --role="roles/pubsub.subscriber" >/dev/null \
  || die "could not grant roles/pubsub.subscriber on $SUB_NAME to $SA_EMAIL"

if [[ ! -f "$KEY_FILE" ]]; then
  gcloud iam service-accounts keys create "$KEY_FILE" --iam-account="$SA_EMAIL" --project="$LOG_PROJECT" \
    || die "could not create a key for $SA_EMAIL"
  chmod 600 "$KEY_FILE"
fi

printf "\n%s✓ Security Command Center setup complete!%s\n" "$G" "$O"
printf "  • Topic:           %s%s%s\n" "$B" "$TOPIC_URI" "$O"
printf "  • Subscription:    %s%s%s\n" "$B" "$SUB_NAME" "$O"
printf "  • Credentials:     %s%s%s\n" "$B" "$KEY_FILE" "$O"
printf "  • Abstract Parser: %sparsers/scc-findings.yml%s (preview; only on the configuration for %s, never on the audit-log one)\n\n" "$C" "$O" "$SUB_NAME"
