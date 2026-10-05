#!/usr/bin/env bash
# =============================================================================
#   Abstract Security — Standalone Google Workspace Reports API Setup
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
  printf "%s   Standalone Google Workspace Reports API Setup (Domain-Wide Delegation)%s\n\n" "$D" "$O"
}

banner

LOG_PROJECT="${1:-}"
ADMIN_EMAIL="${2:-}"

if [[ -z "$LOG_PROJECT" ]]; then
  CURRENT_PROJ=$(gcloud config get-value project 2>/dev/null || true)
  read -r -p "  Enter Logging Project ID [${CURRENT_PROJ}]: " input_proj </dev/tty
  LOG_PROJECT="${input_proj:-$CURRENT_PROJ}"
fi

if [[ -z "$ADMIN_EMAIL" ]]; then
  read -r -p "  Enter Google Workspace Super Admin Email: " ADMIN_EMAIL </dev/tty
fi

[[ -z "$LOG_PROJECT" || -z "$ADMIN_EMAIL" ]] && { echo "Logging Project ID and Admin Email are required."; exit 1; }

SA_NAME="abstract-workspace-reader"
KEY_DIR="$HOME/abstract-keys"
mkdir -p "$KEY_DIR" && chmod 700 "$KEY_DIR"
KEY_FILE="$KEY_DIR/abstract-workspace-key.json"

echo "Enabling admin.googleapis.com on $LOG_PROJECT..."
gcloud services enable admin.googleapis.com --project="$LOG_PROJECT" \
  || die "could not enable admin.googleapis.com on $LOG_PROJECT"

echo "Creating Service Account ($SA_NAME) in $LOG_PROJECT..."
SA_EMAIL="$SA_NAME@$LOG_PROJECT.iam.gserviceaccount.com"
gcloud iam service-accounts describe "$SA_EMAIL" --project="$LOG_PROJECT" >/dev/null 2>&1 \
  || gcloud iam service-accounts create "$SA_NAME" --project="$LOG_PROJECT" \
       --display-name="Abstract Workspace Reports Reader" \
  || die "could not create service account $SA_NAME in $LOG_PROJECT"

CLIENT_ID=$(gcloud iam service-accounts describe "$SA_EMAIL" --project="$LOG_PROJECT" --format="value(uniqueId)") \
  || die "could not read the client ID of $SA_EMAIL"
[[ -n "$CLIENT_ID" ]] || die "empty client ID for $SA_EMAIL"

if [[ ! -f "$KEY_FILE" ]]; then
  gcloud iam service-accounts keys create "$KEY_FILE" --iam-account="$SA_EMAIL" --project="$LOG_PROJECT" \
    || die "could not create a key for $SA_EMAIL"
  chmod 600 "$KEY_FILE"
fi

printf "\n%s━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━%s\n" "$P" "$O"
printf "%sMANDATORY WORKSPACE SUPER ADMIN ACTION (in admin.google.com):%s\n" "$B" "$O"
printf "A Google Workspace Super Admin must grant Domain-Wide Delegation:\n"
printf "  1. Open: %shttps://admin.google.com/ac/owl/domainwidedelegation%s\n" "$C" "$O"
printf "  2. Click %sAdd new%s\n" "$B" "$O"
printf "  3. Enter Client ID: %s%s%s\n" "$B" "$CLIENT_ID" "$O"
printf "  4. Enter OAuth Scopes (comma-separated):\n"
printf "     %shttps://www.googleapis.com/auth/admin.reports.audit.readonly,https://www.googleapis.com/auth/admin.reports.usage.readonly%s\n" "$C" "$O"
printf "  5. Click %sAuthorize%s\n" "$B" "$O"
printf "%s━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━%s\n\n" "$P" "$O"

printf "%s✓ Workspace Service Account & Key Ready!%s\n" "$G" "$O"
printf "  • Client ID:       %s%s%s\n" "$B" "$CLIENT_ID" "$O"
printf "  • Credentials:     %s%s%s\n" "$B" "$KEY_FILE" "$O"
printf "  • Admin Email:     %s%s%s\n" "$B" "$ADMIN_EMAIL" "$O"
printf "  • Abstract:        %sGoogle Workspace integration%s (its managed parser; upload no parser from parsers/)\n\n" "$C" "$O"
