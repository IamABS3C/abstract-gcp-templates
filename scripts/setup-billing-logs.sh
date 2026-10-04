#!/usr/bin/env bash
# =============================================================================
#   Abstract Security — Standalone Cloud Billing Account Audit Setup
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
  printf "%s   Standalone Cloud Billing Account Audit Setup%s\n\n" "$D" "$O"
}

banner

BILLING_ACCOUNT_ID="${1:-}"
LOG_PROJECT="${2:-}"

if [[ -z "$BILLING_ACCOUNT_ID" ]]; then
  DISCOVERED_BA=$(gcloud billing accounts list --filter="open=true" --format="value(name.basename())" 2>/dev/null | head -n1 || true)
  read -r -p "  Enter Billing Account ID [${DISCOVERED_BA}]: " input_ba </dev/tty
  BILLING_ACCOUNT_ID="${input_ba:-$DISCOVERED_BA}"
fi

if [[ -z "$LOG_PROJECT" ]]; then
  CURRENT_PROJ=$(gcloud config get-value project 2>/dev/null || true)
  read -r -p "  Enter Logging Project ID [${CURRENT_PROJ}]: " input_proj </dev/tty
  LOG_PROJECT="${input_proj:-$CURRENT_PROJ}"
fi

[[ -z "$BILLING_ACCOUNT_ID" || -z "$LOG_PROJECT" ]] && { echo "Billing Account ID and Logging Project ID are required."; exit 1; }

TOPIC_NAME="abstract-billing-audit"
SUB_NAME="abstract-billing-audit-sub"
SINK_NAME="abstract-billing-audit-sink"
SA_NAME="abstract-billing-reader"
KEY_DIR="$HOME/abstract-keys"
mkdir -p "$KEY_DIR"
KEY_FILE="$KEY_DIR/abstract-billing-key.json"

echo "Creating Pub/Sub Topic and Subscription in $LOG_PROJECT..."
gcloud pubsub topics create "$TOPIC_NAME" --project="$LOG_PROJECT" 2>/dev/null || true
gcloud pubsub subscriptions create "$SUB_NAME" --topic="$TOPIC_NAME" --project="$LOG_PROJECT" \
  --ack-deadline=60 --message-retention-duration=7d --expiration-period=never 2>/dev/null || true

TOPIC_DEST="pubsub.googleapis.com/projects/$LOG_PROJECT/topics/$TOPIC_NAME"
FILTER='logName:"cloudaudit.googleapis.com%2Factivity" OR logName:"cloudaudit.googleapis.com%2Fsystem_event"'

echo "Creating Billing Account Log Sink ($SINK_NAME)..."
gcloud logging sinks create "$SINK_NAME" "$TOPIC_DEST" \
  --billing-account="$BILLING_ACCOUNT_ID" \
  --log-filter="$FILTER" 2>/dev/null || \
gcloud logging sinks update "$SINK_NAME" "$TOPIC_DEST" \
  --billing-account="$BILLING_ACCOUNT_ID" \
  --log-filter="$FILTER" 2>/dev/null || true

WRITER_IDENTITY=$(gcloud logging sinks describe "$SINK_NAME" --billing-account="$BILLING_ACCOUNT_ID" --format="value(writerIdentity)" 2>/dev/null || true)
if [[ -n "$WRITER_IDENTITY" ]]; then
  echo "Granting roles/pubsub.publisher to Billing Sink Writer Identity ($WRITER_IDENTITY)..."
  gcloud pubsub topics add-iam-policy-binding "$TOPIC_NAME" --project="$LOG_PROJECT" \
    --member="$WRITER_IDENTITY" --role="roles/pubsub.publisher" >/dev/null
fi

echo "Creating Subscriber Service Account ($SA_NAME)..."
gcloud iam service-accounts create "$SA_NAME" --project="$LOG_PROJECT" --display-name="Abstract Billing Reader" 2>/dev/null || true
SA_EMAIL="$SA_NAME@$LOG_PROJECT.iam.gserviceaccount.com"

gcloud pubsub subscriptions add-iam-policy-binding "$SUB_NAME" --project="$LOG_PROJECT" \
  --member="serviceAccount:$SA_EMAIL" --role="roles/pubsub.subscriber" >/dev/null

if [[ ! -f "$KEY_FILE" ]]; then
  gcloud iam service-accounts keys create "$KEY_FILE" --iam-account="$SA_EMAIL" --project="$LOG_PROJECT" 2>/dev/null
  chmod 600 "$KEY_FILE"
fi

printf "\n%s✓ Billing Account Log Export complete!%s\n" "$G" "$O"
printf "  • Billing Account: %s%s%s\n" "$B" "$BILLING_ACCOUNT_ID" "$O"
printf "  • Subscription:    %s%s%s\n" "$B" "$SUB_NAME" "$O"
printf "  • Credentials:     %s%s%s\n\n" "$B" "$KEY_FILE" "$O"
