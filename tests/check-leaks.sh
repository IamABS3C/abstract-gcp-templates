#!/usr/bin/env bash
# This repo is public. Fail on anything that should not be.
#
# Scans GIT-TRACKED FILES ONLY. Walking the working tree instead matched `yum`
# the PACKAGE MANAGER inside downloaded provider changelogs under .terraform/ —
# gitignored files that never ship. Only what is published can leak.
#
# Deliberately bash-3.2 portable (no mapfile): macOS ships bash 3.2, and a check
# that only runs on the CI runner is a check nobody can verify before pushing.
set -uo pipefail
cd "$(dirname "$0")/.." || exit 1

LIST=$(mktemp); trap 'rm -f "$LIST"' EXIT
git ls-files | grep -vE '^(tests/|\.github/)' > "$LIST"

if [ ! -s "$LIST" ]; then
  echo "::error::no tracked files found — is this a git repo?"
  exit 1
fi

fail=0
hit() {
  local what="$1"; shift
  # `xargs -a FILE` is GNU-only — BSD/macOS xargs silently does nothing with it,
  # which made this scanner report "clean" while detecting absolutely nothing.
  # Redirect instead; that is portable.
  if xargs grep -nI "$@" -- < "$LIST" 2>/dev/null; then
    echo "::error::$what"
    fail=1
  fi
}

# Customer names are deliberately NOT listed here — this file is public, and a
# hardcoded list would itself disclose the names it exists to catch.
# Supply them out of band, one extended-regex alternation per line, via either:
#   tests/.leak-names    (untracked; see .gitignore)
#   LEAK_NAME_PATTERNS   (environment variable, same format)
NAMES_FILE="$(dirname "$0")/.leak-names"
if [ -n "${LEAK_NAME_PATTERNS:-}" ]; then
  while IFS= read -r pat; do
    [ -z "$pat" ] && continue
    case "$pat" in \#*) continue ;; esac
    hit "restricted name found" -iE "$pat"
  done <<EOF
$LEAK_NAME_PATTERNS
EOF
elif [ -f "$NAMES_FILE" ]; then
  while IFS= read -r pat; do
    [ -z "$pat" ] && continue
    case "$pat" in \#*) continue ;; esac
    hit "restricted name found" -iE "$pat"
  done < "$NAMES_FILE"
else
  echo "note: no restricted-name list supplied (tests/.leak-names or LEAK_NAME_PATTERNS); name check skipped"
fi

hit "local path found"     -F  '/Users/'
hit "private key found"    -E  'BEGIN .*PRIVATE KEY'
hit "service-account key"  -E  '"type"[[:space:]]*:[[:space:]]*"service_account"'
hit "bearer token"         -iE 'Authorization:[[:space:]]*Bearer[[:space:]]+[A-Za-z0-9._-]{16,}'

if xargs grep -noI -E '\b[0-9]{12}\b' -- < "$LIST" 2>/dev/null | grep -v 123456789012; then
  echo "::error::real-looking numeric ID found"
  fail=1
fi

if [ "$fail" -eq 0 ]; then
  echo "clean — $(wc -l < "$LIST" | tr -d ' ') tracked files scanned"
fi
exit $fail
