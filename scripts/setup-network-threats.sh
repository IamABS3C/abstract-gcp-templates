#!/usr/bin/env bash
# =============================================================================
#   Abstract Security — Standalone Network Threat & Security Telemetry Setup
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
  printf "%s   Standalone Network Threat Telemetry Setup (WAF, IDS, DNS, Firewall)%s\n\n" "$D" "$O"
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

TOPIC_NAME="abstract-network-threats"
SUB_NAME="abstract-network-threats-sub"
SINK_NAME="abstract-network-threats-sink"
SA_NAME="abstract-network-reader"
KEY_DIR="$HOME/abstract-keys"
mkdir -p "$KEY_DIR"
KEY_FILE="$KEY_DIR/abstract-network-key.json"

echo "Creating Dedicated High-Volume Network Topic & Subscription in $LOG_PROJECT..."
gcloud pubsub topics create "$TOPIC_NAME" --project="$LOG_PROJECT" 2>/dev/null || true
gcloud pubsub subscriptions create "$SUB_NAME" --topic="$TOPIC_NAME" --project="$LOG_PROJECT" \
  --ack-deadline=60 --message-retention-duration=7d --expiration-period=never 2>/dev/null || true

TOPIC_DEST="pubsub.googleapis.com/projects/$LOG_PROJECT/topics/$TOPIC_NAME"
FILTER='logName:"compute.googleapis.com%2Ffirewall" OR logName:"dns.googleapis.com%2Fdns_queries" OR resource.type="http_load_balancer" OR logName:"ids.googleapis.com%2Fthreat"'

echo "Creating Aggregated Network Security Log Sink ($SINK_NAME)..."
gcloud logging sinks create "$SINK_NAME" "$TOPIC_DEST" \
  --organization="$ORG_ID" \
  --include-children \
  --log-filter="$FILTER" 2>/dev/null || \
gcloud logging sinks update "$SINK_NAME" "$TOPIC_DEST" \
  --organization="$ORG_ID" \
  --log-filter="$FILTER" 2>/dev/null || true

WRITER_IDENTITY=$(gcloud logging sinks describe "$SINK_NAME" --organization="$ORG_ID" --format="value(writerIdentity)" 2>/dev/null || true)
if [[ -n "$WRITER_IDENTITY" ]]; then
  echo "Granting roles/pubsub.publisher to Network Sink Writer Identity ($WRITER_IDENTITY)..."
  gcloud pubsub topics add-iam-policy-binding "$TOPIC_NAME" --project="$LOG_PROJECT" \
    --member="$WRITER_IDENTITY" --role="roles/pubsub.publisher" >/dev/null
fi

echo "Creating Subscriber Service Account ($SA_NAME)..."
gcloud iam service-accounts create "$SA_NAME" --project="$LOG_PROJECT" --display-name="Abstract Network Telemetry Reader" 2>/dev/null || true
SA_EMAIL="$SA_NAME@$LOG_PROJECT.iam.gserviceaccount.com"

gcloud pubsub subscriptions add-iam-policy-binding "$SUB_NAME" --project="$LOG_PROJECT" \
  --member="serviceAccount:$SA_EMAIL" --role="roles/pubsub.subscriber" >/dev/null

if [[ ! -f "$KEY_FILE" ]]; then
  gcloud iam service-accounts keys create "$KEY_FILE" --iam-account="$SA_EMAIL" --project="$LOG_PROJECT" 2>/dev/null
  chmod 600 "$KEY_FILE"
fi

printf "\n%s✓ Network Threat Telemetry Setup complete!%s\n" "$G" "$O"
printf "  • Subscription:    %s%s%s\n" "$B" "$SUB_NAME" "$O"
printf "  • Credentials:     %s%s%s\n" "$B" "$KEY_FILE" "$O"
printf "  • Filter includes: Cloud Armor WAF, Cloud IDS, Cloud DNS, and Firewall rules\n\n"
