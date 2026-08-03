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
scripts/verify_release.py     Offline repository verifier
tests/test_guard_decision.py  Standard-library rule tests
release/                      Public manifest and inventory
SHA256SUMS                    Repository file checksums
```

The Skill directory itself contains only `SKILL.md`, `agents/openai.yaml`, the deterministic helper, and three references. It contains no website, frontend, model output, private gold, credentials, or research dataset.

## Validate locally

```bash
python3 -m unittest discover -s tests -v
python3 scripts/verify_release.py
```

Both commands are offline and require only Python's standard library. The Skill helper accepts one JSON object on stdin:

```bash
python3 memory-applicability-guard/scripts/guard_decision.py < guard-input.json
```

## Install from GitHub after publication

Once this repository has an owner/repository URL, install the Skill with the official installer by pointing it to the `memory-applicability-guard` subdirectory. Do not install from an unreviewed fork.

## Research boundary

The frozen v0.7 experiment ended at `STOP_AT_V07`: A0 and M1 both scored 110/128, matched net improvement was 0, strict-twin stable flips were 28/40 for A0 and 27/40 for M1, and ASK recall was 60% for both. This prototype translates research concepts into an auditable workflow; it did not beat the baseline and does not provide a production safety guarantee.

Do not use it to autonomously approve medical, legal, financial, employment, insurance, housing, privacy, or safety-critical decisions. High-risk input is escalated for human review.

## Publication and license status

This local repository is prepared for GitHub review but has not been pushed or published. A license has not yet been selected; see `LICENSE`. Public publication should remain blocked until the repository owner explicitly chooses the license and approves the remote destination and visibility.
