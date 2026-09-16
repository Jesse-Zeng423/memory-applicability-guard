#!/usr/bin/env python3
"""Run synthetic guard scenarios and print a transparent outcome table.

Decision support only; not production validated. This harness does not claim
accuracy improvement, production safety, or deployment readiness.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HELPER = ROOT / "memory-applicability-guard/scripts/guard_decision.py"
EXAMPLE_DIR = ROOT / "schema/examples"
EXTRA_DIR = ROOT / "benchmarks/scenarios"


def _load_helper():
    spec = importlib.util.spec_from_file_location("guard_decision", HELPER)
    if spec is None or spec.loader is None:
        raise SystemExit(f"unable to load helper from {HELPER}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def scenario_paths() -> list[Path]:
    paths = sorted(EXAMPLE_DIR.glob("*.json"))
    if EXTRA_DIR.is_dir():
        paths.extend(sorted(EXTRA_DIR.glob("*.json")))
    return paths


def run_scenarios(guard) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for path in scenario_paths():
        payload = json.loads(path.read_text(encoding="utf-8"))
        result = guard.decide(payload)
        rows.append(
            {
                "scenario": path.relative_to(ROOT).as_posix(),
                "proposed_memory_action": payload["proposed_memory_action"],
                "guard_verdict": result["guard_verdict"],
                "memory_action": result["memory_action"],
                "memory_state": result["memory_state"],
                "reason_code": result["reason_code"],
            }
        )
    return rows


def render_markdown(rows: list[dict[str, object]]) -> str:
    lines = [
        "# Synthetic guard outcomes",
        "",
        "Decision support only; not production validated.",
        "",
        "| Scenario | Proposed | Verdict | Memory action | State | Reason |",
        "|---|---|---|---|---|---|",
    ]
    for row in rows:
        lines.append(
            "| `{scenario}` | `{proposed_memory_action}` | `{guard_verdict}` | "
            "`{memory_action}` | `{memory_state}` | `{reason_code}` |".format(**row)
        )
    lines.append("")
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Run synthetic Memory Applicability Guard scenarios. "
            "Decision support only; not production validated."
        )
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of markdown")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    guard = _load_helper()
    rows = run_scenarios(guard)
    if args.json:
        print(json.dumps({"boundary": guard.BOUNDARY, "results": rows}, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(render_markdown(rows), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
