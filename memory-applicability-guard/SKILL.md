---
name: memory-applicability-guard
description: Audit whether a candidate memory should inform an Agent's recommendation or action, and return PASS, REVISE, ASK_USER, VERIFY_EXTERNAL, or ESCALATE with a structured USE/IGNORE/ASK decision. Use for memory-grounded recommendation, personalization audit, USE/IGNORE/ASK review, superseded memory, cross-domain transfer, permission revocation, evidence gaps, and robust-action analysis. This is a research-informed decision-support prototype, not a production-validated autonomous guard.
---

# Memory Applicability Guard

## Goal

Review a supplied candidate memory before an Agent relies on it. Treat the result as decision support only; never execute or silently rewrite the Agent's answer.

## Extract input

1. Identify `current_task` and `candidate_memory` from supplied context.
2. Record the Agent's `proposed_memory_action` as `USE`, `IGNORE`, or `ASK`.
3. Classify explicit `permission`, `relationship`, `evidence_status`, `risk`, and robust-action availability.
4. Preserve evidence IDs and mark only current boundary evidence as decisive. Never treat memory provenance as applicability evidence.
5. If these structured fields cannot be supported by supplied evidence, label them `UNKNOWN`; do not infer transfer from relevance or similarity.

Read `references/decision-model.md` whenever classifying inputs or explaining precedence. Read `references/examples.md` for synthetic examples or calibration. Read `references/research-boundaries.md` before high-risk use, product claims, deployment discussion, or reporting frozen metrics.

## Decide

Apply this order:

1. Revoked permission: ignore the memory.
2. High risk: escalate to human review.
3. Required current or third-party evidence: verify externally; never ask the user to guess live facts.
4. `NO_BRIDGE` or `SUPERSEDED`: ignore the memory.
5. Allowed, sufficiently evidenced `DIRECT` or `EXPLICIT_TRANSFER`: use the memory.
6. User-resolvable, action-changing uncertainty without a robust action: ask the user.
7. Robust action across reasonable worlds: ignore the disputed memory and take the named robust action without asking.
8. Other evidence gaps: ask for clarification; never default to USE.

## Run deterministic helper

Pass one JSON object on stdin, or use `--file`:

```bash
python3 scripts/guard_decision.py < guard-input.json
python3 scripts/guard_decision.py --file guard-input.json --pretty
python3 scripts/guard_decision.py --validate-only --file guard-input.json
python3 scripts/guard_decision.py --schema
```

Use the helper only after extracting explicit structured inputs. Treat its JSON as a recommendation, not an automatic edit. If validation fails, correct the input using the stderr `issues` list; never weaken validation.

## Respond

Return exactly these fields from the helper:

- `guard_verdict`
- `memory_action`
- `memory_state`
- `resolution_source`
- `decisive_evidence`
- `reason_code`
- `next_step`
- `boundary`

Keep `memory_action` separate from the underlying task action. Make the research/product boundary visible in every result.

## Hard rules

- Relevance is not applicability; similarity is not explicit transfer.
- Memory provenance is not applicability evidence.
- Truth is not permission; citation is not correct evidence use.
- Conservative behavior is not always ASK; prefer a supplied robust action.
- Do not browse, call APIs, read credentials, access private gold, or retrieve hidden memories through this Skill.
- Do not modify the Agent's original output or execute the proposed action.
- Do not approve medical, legal, financial, employment, insurance, housing, privacy, or safety-critical actions. Escalate high risk.
- Never claim accuracy improvement, production validation, autonomous safety, or deployment readiness.

## Research boundary

Describe the capability as: **Research-informed Memory Applicability Guard — Decision support only; not production validated.** Preserve `STOP_AT_V07`; the Skill operationalizes an auditable review workflow but does not overturn the frozen negative result.
