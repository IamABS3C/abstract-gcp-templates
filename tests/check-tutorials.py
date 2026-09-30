#!/usr/bin/env python3
"""Assert every command in a TUTORIAL.md still matches the code.

Tutorials drift silently. An output gets renamed and the tutorial keeps naming the
old one, which fails only when a customer runs it — which is how it should never
be discovered. This repo shipped exactly that: `gcs_service_agent` became
`gcs_service_agents` when multi-project support landed, plus two uses of
`terraform output -raw` on OBJECT outputs, which errors outright.

Checks:
  1. every `terraform output X` names an output that exists in that deployment
  2. `-raw` is only used on outputs that are plain strings
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DEPLOYMENTS = ROOT / "deployments"


def declared_outputs(d: pathlib.Path) -> dict[str, str]:
    """output name -> its value expression."""
    f = d / "outputs.tf"
    if not f.exists():
        return {}
    text = f.read_text()
    out = {}
    # Two forms in the wild, and matching only the multi-line one produced three
    # false positives ("has: none") on files that declare outputs perfectly well:
    #   output "x" { value = y }                 <- single line
    #   output "x" {\n  value = y\n}              <- block
    for m in re.finditer(r'output "([a-z_]+)"\s*\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}',
                         text, re.S):
        out[m.group(1)] = m.group(2)
    return out


def looks_like_object(value_expr: str) -> bool:
    """A value that is not a plain string cannot be read with -raw."""
    return bool(re.search(r"=\s*\{|_onboarding|preflight|alert_policies|"
                          r"service_agents|selected_log_sources|volume_profile|"
                          r"notification_ids|enabled\b", value_expr))


def main() -> int:
    problems = []
    for tut in sorted(DEPLOYMENTS.glob("*/TUTORIAL.md")):
        body = tut.read_text()
        for m in re.finditer(r"terraform output (-raw |-json )?([A-Za-z0-9_]+)", body):
            flag = (m.group(1) or "").strip()
            name = m.group(2)

            # A preceding `cd ../NN-name` means the output belongs to that deployment.
            before = body[max(0, m.start() - 200):m.start()]
            hops = re.findall(r"cd \.\./(\d\d-[a-z-]+)", before)
            target = DEPLOYMENTS / (hops[-1] if hops else tut.parent.name)

            outs = declared_outputs(target)
            rel = tut.relative_to(ROOT)
            if name not in outs:
                problems.append(
                    f"{rel}: `terraform output {name}` — no such output in "
                    f"{target.name} (has: {', '.join(sorted(outs)) or 'none'})")
            elif flag == "-raw" and looks_like_object(outs[name]):
                problems.append(
                    f"{rel}: `terraform output -raw {name}` — -raw fails on a "
                    f"non-string output. Use `-json {name} | jq -r .field`")

    for p in problems:
        print(f"::error::{p}")
    print(f"{'FAIL' if problems else 'ok'}: {len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
