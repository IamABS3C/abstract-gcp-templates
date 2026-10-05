#!/usr/bin/env bash
# This repo is public. Fail on anything that should not be.
#
# Scans GIT-TRACKED FILES ONLY. Walking the working tree instead matched `yum`
# the PACKAGE MANAGER inside downloaded provider changelogs under .terraform/ —
# gitignored files that never ship. Only what is published can leak.
#
# FAILS CLOSED. A scanner that cannot read a file must fail, not report "clean".
# It once did exactly that: a tracked symlink to a directory made grep exit 2,
# xargs then returned 123, and every check read that as "no match" while printing
# the leak. So: tracked symlinks are refused outright, each grep batch maps its own
# status (0/1 = ran, a hit is decided by output; 2+ = error), and any error fails.
#
# Deliberately bash-3.2 portable (no mapfile): macOS ships bash 3.2, and a check
# that only runs on the CI runner is a check nobody can verify before pushing.
set -uo pipefail
cd "$(dirname "$0")/.." || exit 1

LIST=$(mktemp "${TMPDIR:-/tmp}/check-leaks.XXXXXX") || { echo "::error::mktemp failed"; exit 1; }
trap 'rm -f "$LIST"' EXIT

fail=0
count=0
# `git ls-files -s -z`: "<mode> <sha> <stage>\t<path>\0". NUL-safe for any file name.
while IFS= read -r -d '' entry; do
  mode=${entry%% *}
  path=${entry#*$'\t'}
  case "$path" in tests/*|.github/*) continue ;; esac
  if [ "$mode" = "120000" ]; then
    echo "::error::tracked symlink $path — symlinks are not published and blind this scanner; remove it"
    fail=1
    continue
  fi
  printf '%s\0' "$path" >> "$LIST"
  count=$((count + 1))
done < <(git ls-files -s -z) || true

if ! git rev-parse --git-dir >/dev/null 2>&1 || [ "$count" -eq 0 ]; then
  echo "::error::no tracked files found — is this a git repo?"
  exit 1
fi

# scan <grep args...>: print every match; return 0 when grep RAN on every file
# (hit or no hit), non-zero when any grep could not run. xargs returns 123 for any
# batch exit 1-125, which would conflate "no match" with "error", so each batch maps
# grep's status itself: 0 or 1 -> 0, 2+ -> 255, which makes xargs stop with 124.
scan() {
  xargs -0 sh -c 'grep -nHI "$@"; r=$?; [ "$r" -le 1 ] || exit 255' sh "$@" -- < "$LIST"
}

hit() {
  local what="$1"; shift
  local out rc
  out=$(scan "$@"); rc=$?
  if [ "$rc" -ne 0 ]; then
    echo "::error::scan failed (xargs/grep exit $rc) while checking: $what — failing closed"
    fail=1
  fi
  if [ -n "$out" ]; then
    printf '%s\n' "$out"
    echo "::error::$what"
    fail=1
  fi
}

# Customer names are deliberately NOT listed here — this file is public, and a
# hardcoded list would itself disclose the names it exists to catch.
# Supply them out of band, one extended-regex alternation per line, via either:
#   tests/.leak-names    (untracked; ignored in .gitignore)
#   LEAK_NAME_PATTERNS   (environment variable, same format)
NAMES_FILE="$(dirname "$0")/.leak-names"
if [ -n "${LEAK_NAME_PATTERNS:-}" ]; then
  while IFS= read -r pat; do
    [ -z "$pat" ] && continue
    case "$pat" in \#*) continue ;; esac
    hit "restricted name found" -iE "$pat"
  done <<NAMES
$LEAK_NAME_PATTERNS
NAMES
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

ids=$(scan -oE '\b[0-9]{12}\b'); rc=$?
if [ "$rc" -ne 0 ]; then
  echo "::error::scan failed (xargs/grep exit $rc) while checking numeric IDs — failing closed"
  fail=1
fi
ids=$(printf '%s\n' "$ids" | grep -v ':123456789012$' | grep -v '^$' || true)
if [ -n "$ids" ]; then
  printf '%s\n' "$ids"
  echo "::error::real-looking numeric ID found"
  fail=1
fi

if [ "$fail" -eq 0 ]; then
  echo "clean — $count tracked files scanned"
fi
exit $fail
