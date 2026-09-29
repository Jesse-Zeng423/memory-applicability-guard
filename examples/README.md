# Runnable examples

All people, preferences, and evidence here are synthetic. Run from the repository root:

```bash
python3 -B examples/run_examples.py
```

| Case | Expected decision | What it illustrates |
| --- | --- | --- |
| `superseded-preference` | `REVISE / IGNORE` | A current instruction overrides an older preference. |
| `explicit-transfer` | `REVISE / USE` | Explicit user transfer supports reuse in a new context. |
| `robust-alternative` | `REVISE / IGNORE` | A useful reversible draft avoids relying on disputed memory. |

Each case is a three-part demonstration: `.scenario.md` describes the natural-language situation, `.input.json` provides the expected classification, and `.expected.json` records the helper result. The runner executes the helper and compares the complete parsed output, including evidence and boundary text. These snapshots document the API; independent rule and precedence assertions live in `tests/`.

Run one example directly:

```bash
python3 -B memory-applicability-guard/scripts/guard_decision.py < examples/explicit-transfer.input.json
```

The expected file can be inspected beside the output. No model or external service is involved.
