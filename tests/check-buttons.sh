#!/usr/bin/env bash
# Every Cloud Shell button must point at a tutorial that exists AT THE PATH
# CLOUD SHELL RESOLVES.
#
# cloudshell_tutorial is relative to cloudshell_workspace, not to the repo root.
# This repo shipped that bug in every button, and it 404s only at click time —
# checking the raw GitHub URL does not catch it, because that path exists, it is
# just not the one Cloud Shell uses.
set -uo pipefail
# cloudshell_workspace is resolved by Cloud Shell relative to the ROOT of the cloned
# repo -- not to this script. Anchor there so the check is correct whether this tree
# is the repo root or vendored under templates/. export/ holds README templates for other
# repositories, whose paths only resolve there; the export's own run checks them.
ROOT="$(git -C "$(dirname "$0")" rev-parse --show-toplevel 2>/dev/null)"
[ -z "$ROOT" ] && ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT" || exit 1

fail=0
found=0
while read -r ws tut; do
  found=$((found + 1))
  if [ -f "$ws/$tut" ]; then
    echo "  ok       $ws/$tut"
  else
    echo "::error::missing $ws/$tut"
    fail=1
  fi
done < <(grep -rhoE 'cloudshell_workspace=[^&"]+&cloudshell_tutorial=[^"&)]+' \
           $(git ls-files '*README.md' '*TUTORIAL.md' ':!export/*' 2>/dev/null | tr '\n' ' ') 2>/dev/null \
         | sed -E 's|cloudshell_workspace=([^&]+)&cloudshell_tutorial=(.+)|\1 \2|' \
         | sort -u)

if [ "$found" -eq 0 ]; then
  echo "::error::no buttons found at all — the regex or the README changed shape"
  exit 1
fi

# Cloud Shell clones branch `master` unless told otherwise, and this repository has only
# `main`: a link without cloudshell_git_branch opens an empty shell with nothing cloned.
nobranch=$(grep -rhoE 'cloudshell_git_repo=[^")[:space:]]+' \
             $(git ls-files '*.md' 2>/dev/null | tr '\n' ' ') 2>/dev/null \
           | grep -v 'cloudshell_git_branch=' | sort -u)
if [ -n "$nobranch" ]; then
  echo "::error::Cloud Shell link(s) without cloudshell_git_branch (Cloud Shell would clone master):"
  printf '    %s\n' $nobranch
  fail=1
fi

echo "  $found button target(s), $( [ "$fail" -eq 0 ] && echo "all resolve" || echo "SOME MISSING" )"
exit $fail
