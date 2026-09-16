# Synthetic decision examples

Decision support only; not production validated.

This directory is a tiny public harness for the frozen research boundary (`STOP_AT_V07`). It reruns checked-in synthetic scenarios through the deterministic helper and prints a markdown table of outcomes. It does not claim accuracy gains, production safety, or deployment readiness.

## Run

```bash
python3 scripts/run_benchmark.py
python3 scripts/run_benchmark.py --json
```

By default the runner uses `schema/examples/*.json` plus any extra files under `benchmarks/scenarios/`. Extra scenarios are optional edge cases that keep the example set readable while still covering multi-evidence and conflicting-permission shapes.

## Interpreting results

Each row reports `guard_verdict`, `memory_action`, `memory_state`, and `reason_code`. `PASS` means the proposed memory action already matches the helper recommendation; it never approves the underlying task.
