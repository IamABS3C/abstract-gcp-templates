#!/usr/bin/env bash
# Open architecture diagrams in Draw.io Desktop (macOS / Linux) or diagrams.net
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

if [ $# -lt 1 ]; then
  echo "Usage: $0 <diagram-name> [--web]"
  echo "Example: $0 01-logging-project"
  echo "         $0 02-audit-logs-organization --web"
  exit 1
fi

NAME="$1"
WEB_MODE=0
if [ "${2:-}" = "--web" ]; then
  WEB_MODE=1
elif [ "$1" = "--web" ]; then
  WEB_MODE=1
  NAME="${2:-}"
  if [ -z "$NAME" ]; then
    echo "Usage: $0 --web <diagram-name>"
    exit 1
  fi
fi

# Strip directory path and extension if passed
BASENAME="$(basename "$NAME" .drawio)"
BASENAME="$(basename "$BASENAME" .png)"
BASENAME="$(basename "$BASENAME" .svg)"

# Locate .drawio file
CANDIDATE=""
for search_dir in "$REPO_ROOT/images/diagrams" "$REPO_ROOT/diagrams"; do
  if [ -f "$search_dir/$BASENAME.drawio" ]; then
    CANDIDATE="$search_dir/$BASENAME.drawio"
    break
  elif [ -f "$search_dir/$NAME" ]; then
    CANDIDATE="$search_dir/$NAME"
    break
  fi
done

if [ -z "$CANDIDATE" ]; then
  echo "Error: Diagram '$NAME' (or '$BASENAME.drawio') not found in images/diagrams/ or diagrams/"
  exit 1
fi

if [ "$WEB_MODE" -eq 1 ]; then
  echo "Opening $CANDIDATE in diagrams.net..."
  if command -v open >/dev/null 2>&1; then
    open "https://app.diagrams.net/"
  elif command -v xdg-open >/dev/null 2>&1; then
    xdg-open "https://app.diagrams.net/"
  else
    echo "Open https://app.diagrams.net/ and load $CANDIDATE"
  fi
  exit 0
fi

# Desktop mode
if [[ "$OSTYPE" == "darwin"* ]]; then
  if [ -d "/Applications/draw.io.app" ]; then
    open -a "draw.io" "$CANDIDATE"
  else
    open "$CANDIDATE"
  fi
elif command -v drawio >/dev/null 2>&1; then
  drawio "$CANDIDATE" &
elif command -v xdg-open >/dev/null 2>&1; then
  xdg-open "$CANDIDATE"
else
  echo "Draw.io diagram located at: $CANDIDATE"
  echo "Open this file in Draw.io Desktop (https://www.drawio.com/)."
fi
