#!/usr/bin/env bash
# =============================================================================
#   Abstract Security — Standalone Security Command Center (SCC) Findings Setup
# =============================================================================
set -uo pipefail

B=$'\033[1m'; P=$'\033[38;5;198m'; G=$'\033[0;32m'; Y=$'\033[0;33m'; R=$'\033[0;31m'; C=$'\033[0;36m'; D=$'\033[2m'; O=$'\033[0m'
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
mkdir -p "$KEY_DIR"
KEY_FILE="$KEY_DIR/abstract-scc-key.json"

echo "Creating Pub/Sub Topic and Subscription in $LOG_PROJECT..."
gcloud pubsub topics create "$TOPIC_NAME" --project="$LOG_PROJECT" 2>/dev/null || true
gcloud pubsub subscriptions create "$SUB_NAME" --topic="$TOPIC_NAME" --project="$LOG_PROJECT" \
  --ack-deadline=60 --message-retention-duration=7d --expiration-period=never 2>/dev/null || true

TOPIC_URI="projects/$LOG_PROJECT/topics/$TOPIC_NAME"
SCC_AGENT="serviceAccount:service-org-$ORG_ID@gcp-sa-scc-notification.iam.gserviceaccount.com"

echo "Granting roles/pubsub.publisher on topic to SCC Service Agent ($SCC_AGENT)..."
gcloud pubsub topics add-iam-policy-binding "$TOPIC_NAME" --project="$LOG_PROJECT" \
  --member="$SCC_AGENT" --role="roles/pubsub.publisher" >/dev/null

echo "Configuring SCC Organization NotificationConfig ($NOTIF_ID)..."
gcloud scc notifications create "$NOTIF_ID" \
  --organization="$ORG_ID" \
  --pubsub-topic="$TOPIC_URI" \
  --description="Abstract Security real-time finding notifications" \
  --filter="state=\"ACTIVE\"" 2>/dev/null || \
gcloud scc notifications update "$NOTIF_ID" \
  --organization="$ORG_ID" \
  --pubsub-topic="$TOPIC_URI" 2>/dev/null || true

echo "Creating Subscriber Service Account ($SA_NAME)..."
gcloud iam service-accounts create "$SA_NAME" --project="$LOG_PROJECT" --display-name="Abstract SCC Reader" 2>/dev/null || true
SA_EMAIL="$SA_NAME@$LOG_PROJECT.iam.gserviceaccount.com"

gcloud pubsub subscriptions add-iam-policy-binding "$SUB_NAME" --project="$LOG_PROJECT" \
  --member="serviceAccount:$SA_EMAIL" --role="roles/pubsub.subscriber" >/dev/null

if [[ ! -f "$KEY_FILE" ]]; then
  gcloud iam service-accounts keys create "$KEY_FILE" --iam-account="$SA_EMAIL" --project="$LOG_PROJECT" 2>/dev/null
  chmod 600 "$KEY_FILE"
fi

printf "\n%s✓ Security Command Center setup complete!%s\n" "$G" "$O"
printf "  • Topic:           %s%s%s\n" "$B" "$TOPIC_URI" "$O"
printf "  • Subscription:    %s%s%s\n" "$B" "$SUB_NAME" "$O"
printf "  • Credentials:     %s%s%s\n" "$B" "$KEY_FILE" "$O"
printf "  • Abstract Parser: %sparsers/scc-findings.yml%s\n\n" "$C" "$O"
