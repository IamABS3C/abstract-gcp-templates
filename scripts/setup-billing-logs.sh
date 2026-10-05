#!/usr/bin/env bash
# =============================================================================
#   Abstract Security — Standalone Cloud Billing Account Audit Setup
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
mkdir -p "$KEY_DIR" && chmod 700 "$KEY_DIR"
KEY_FILE="$KEY_DIR/abstract-billing-key.json"

echo "Creating Pub/Sub Topic and Subscription in $LOG_PROJECT..."
gcloud pubsub topics describe "$TOPIC_NAME" --project="$LOG_PROJECT" >/dev/null 2>&1 \
  || gcloud pubsub topics create "$TOPIC_NAME" --project="$LOG_PROJECT" \
  || die "could not create topic $TOPIC_NAME in $LOG_PROJECT"
gcloud pubsub subscriptions describe "$SUB_NAME" --project="$LOG_PROJECT" >/dev/null 2>&1 \
  || gcloud pubsub subscriptions create "$SUB_NAME" --topic="$TOPIC_NAME" --project="$LOG_PROJECT" \
       --ack-deadline=60 --message-retention-duration=7d --expiration-period=never \
  || die "could not create subscription $SUB_NAME in $LOG_PROJECT"

TOPIC_DEST="pubsub.googleapis.com/projects/$LOG_PROJECT/topics/$TOPIC_NAME"
FILTER='logName:"cloudaudit.googleapis.com%2Factivity" OR logName:"cloudaudit.googleapis.com%2Fsystem_event"'

echo "Creating Billing Account Log Sink ($SINK_NAME)..."
# deployments/10-billing-account creates a sink with this SAME name, pointed at a different
# topic. Updating it here would repoint that sink and silently cut off the Terraform
# pipeline, so refuse unless the existing sink is this script's own.
EXISTING_DEST=""
if EXISTING_DEST=$(gcloud logging sinks describe "$SINK_NAME" --billing-account="$BILLING_ACCOUNT_ID" --format="value(destination)" 2>/dev/null); then
  if [[ "$EXISTING_DEST" != "$TOPIC_DEST" ]]; then
    die "sink $SINK_NAME already exists on billing account $BILLING_ACCOUNT_ID and sends to $EXISTING_DEST.
  It is most likely managed by deployments/10-billing-account. This script would repoint it.
  Manage it there instead:  cd deployments/10-billing-account && terraform apply"
  fi
  gcloud logging sinks update "$SINK_NAME" "$TOPIC_DEST" \
    --billing-account="$BILLING_ACCOUNT_ID" --log-filter="$FILTER" \
    || die "could not update sink $SINK_NAME"
else
  gcloud logging sinks create "$SINK_NAME" "$TOPIC_DEST" \
    --billing-account="$BILLING_ACCOUNT_ID" --log-filter="$FILTER" \
    || die "could not create sink $SINK_NAME on billing account $BILLING_ACCOUNT_ID (needs roles/logging.configWriter there)"
fi

WRITER_IDENTITY=$(gcloud logging sinks describe "$SINK_NAME" --billing-account="$BILLING_ACCOUNT_ID" --format="value(writerIdentity)") \
  || die "could not read the writer identity of $SINK_NAME"
[[ -n "$WRITER_IDENTITY" ]] || die "sink $SINK_NAME has no writer identity"
echo "Granting roles/pubsub.publisher to Billing Sink Writer Identity ($WRITER_IDENTITY)..."
gcloud pubsub topics add-iam-policy-binding "$TOPIC_NAME" --project="$LOG_PROJECT" \
  --member="$WRITER_IDENTITY" --role="roles/pubsub.publisher" >/dev/null \
  || die "could not grant roles/pubsub.publisher on $TOPIC_NAME to $WRITER_IDENTITY"

echo "Creating Subscriber Service Account ($SA_NAME)..."
SA_EMAIL="$SA_NAME@$LOG_PROJECT.iam.gserviceaccount.com"
gcloud iam service-accounts describe "$SA_EMAIL" --project="$LOG_PROJECT" >/dev/null 2>&1 \
  || gcloud iam service-accounts create "$SA_NAME" --project="$LOG_PROJECT" --display-name="Abstract Billing Reader" \
  || die "could not create service account $SA_NAME in $LOG_PROJECT"

gcloud pubsub subscriptions add-iam-policy-binding "$SUB_NAME" --project="$LOG_PROJECT" \
  --member="serviceAccount:$SA_EMAIL" --role="roles/pubsub.subscriber" >/dev/null \
  || die "could not grant roles/pubsub.subscriber on $SUB_NAME to $SA_EMAIL"

if [[ ! -f "$KEY_FILE" ]]; then
  gcloud iam service-accounts keys create "$KEY_FILE" --iam-account="$SA_EMAIL" --project="$LOG_PROJECT" \
    || die "could not create a key for $SA_EMAIL"
  chmod 600 "$KEY_FILE"
fi

printf "\n%s✓ Billing Account Log Export complete!%s\n" "$G" "$O"
printf "  • Billing Account: %s%s%s\n" "$B" "$BILLING_ACCOUNT_ID" "$O"
printf "  • Subscription:    %s%s%s\n" "$B" "$SUB_NAME" "$O"
printf "  • Credentials:     %s%s%s\n\n" "$B" "$KEY_FILE" "$O"
