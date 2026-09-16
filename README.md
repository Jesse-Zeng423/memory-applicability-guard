# Memory Applicability Guard

> Research-informed decision support for reviewing whether a candidate memory should influence an Agent's recommendation or action.

**Decision support only; not production validated.**

This repository contains an installable Codex Skill and a deterministic, standard-library Python helper. It reviews explicit structured inputs and recommends one of:

- `PASS`
- `REVISE`
- `ASK_USER`
- `VERIFY_EXTERNAL`
- `ESCALATE`

The result also separates `memory_action` (`USE | IGNORE | ASK`) from the underlying task action and reports memory state, resolution source, decisive evidence, reason code, next step, and the research/product boundary.

## Why this exists

Retrieved or relevant memory is not automatically applicable. Current scope, permission, newer evidence, external facts, and robust alternatives can change whether an Agent should rely on an old memory.

The Skill makes these distinctions explicit:

- relevance ≠ applicability;
- provenance ≠ applicability evidence;
- truth ≠ permission;
- similarity ≠ explicit transfer;
- uncertainty ≠ always ASK.

## Repository layout

```text
memory-applicability-guard/   Installable Skill package
pyproject.toml                Optional Python package metadata and CLI entry point
src/                          Thin installable wrapper around the Skill helper
schema/                       JSON Schema and contract examples
scripts/verify_release.py     Offline repository verifier
tests/                        Standard-library rule, schema, and packaging tests
release/                      Public manifest and inventory
SHA256SUMS                    Repository file checksums
LICENSE_SCOPE.md              File-category license mapping
LICENSES/                     Apache-2.0 and CC BY 4.0 full texts
```

The Skill directory itself contains only `SKILL.md`, `agents/openai.yaml`, the deterministic helper, and three references. It contains no website, frontend, model output, private gold, credentials, or research dataset.

## Validate locally

```bash
python3 -m unittest discover -s tests -v
python3 scripts/verify_release.py
```

Both commands are offline and require only Python's standard library. The Skill helper accepts one JSON object on stdin, or from a file:

```bash
python3 memory-applicability-guard/scripts/guard_decision.py < guard-input.json
python3 memory-applicability-guard/scripts/guard_decision.py --file guard-input.json --pretty
python3 memory-applicability-guard/scripts/guard_decision.py --validate-only --file guard-input.json
python3 memory-applicability-guard/scripts/guard_decision.py --schema
```

Invalid payloads still fail closed: the helper prints a JSON object on stderr with `error`, `details`, and an `issues` list, then exits `2`. `--schema` prints the closed input contract; `--validate-only` checks that contract without producing a decision. The same contract is checked in at `schema/guard-input.schema.json`, with worked examples in `schema/examples/`.

## Install the Python helper

The Skill directory remains a standalone Codex Skill. Optionally install the same helper as a Python package from a repository clone:

```bash
python3 -m pip install -e .
python3 -m memory_applicability_guard --file schema/examples/superseded-pool.json --pretty
```

The installable package wraps the Skill helper; it does not copy or change the decision rules. This is a research-informed prototype. Installing it does not add a production safety guarantee.

## Install from GitHub after publication

Once this repository has an owner/repository URL, install the Skill with the official installer by pointing it to the `memory-applicability-guard` subdirectory. Do not install from an unreviewed fork.

## Research boundary

The frozen v0.7 experiment ended at `STOP_AT_V07`: A0 and M1 both scored 110/128, matched net improvement was 0, strict-twin stable flips were 28/40 for A0 and 27/40 for M1, and ASK recall was 60% for both. This prototype translates research concepts into an auditable workflow; it did not beat the baseline and does not provide a production safety guarantee.

Do not use it to autonomously approve medical, legal, financial, employment, insurance, housing, privacy, or safety-critical decisions. High-risk input is escalated for human review.

## Publication status

The public repository is available at
[`Jesse-Zeng423/memory-applicability-guard`](https://github.com/Jesse-Zeng423/memory-applicability-guard).
The repository owner has confirmed completion of human review. The release
remains a research-informed decision-support prototype; publication and review
completion do not constitute production validation.

## License

This repository uses a dual-license model:

- Code, scripts, schemas, validators, evaluators, tests, and the complete
  `memory-applicability-guard/` Skill package are licensed under the Apache
  License 2.0.
- Research reports, repository documentation, diagrams, presentation
  materials, synthetic examples outside the Skill package, and public
  evaluation data are licensed under Creative Commons Attribution 4.0
  International (CC BY 4.0).
- Private gold labels, credentials, unpublished research artifacts, and
  third-party materials are not included in these grants.

See `LICENSE_SCOPE.md` for the controlling scope statement, `LICENSE` and
`LICENSES/Apache-2.0.txt` for Apache-2.0, and
`LICENSES/CC-BY-4.0.txt` for CC BY 4.0.
