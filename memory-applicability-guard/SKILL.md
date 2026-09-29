---
name: memory-applicability-guard
description: Review whether supplied candidate memory may inform a current action. Use for scope, permission, conflicting evidence, and explicit transfer audits before memory reliance.
---

# Memory Applicability Guard

## When to use

Use after retrieval and before response generation when candidate memories,
current task context, and evidence metadata are exposed. Audit one memory
and its proposed `USE`, `IGNORE`, or `ASK` action per call.

## When not to use

Do not use for retrieval, memory storage, factual verification, generic advice,
or a task with no identifiable candidate memory. Do not invent hidden memories
or promise coverage when required context and metadata are unavailable.

## Workflow

### 1. Establish the audit

Identify the supplied `current_task`, `candidate_memory`, and
`proposed_memory_action`. Keep the underlying task separate from memory reliance.
Done when the memory and proposed action are explicit; otherwise request only
what is needed to identify them.

### 2. Classify from evidence

Read [classification-rubric.md](references/classification-rubric.md) before
classification. Build the closed input in [decision-model.md](references/decision-model.md).
Follow evidence → permission → risk → evidence status → relationship → robust action.
Preserve supplied IDs and text. Mark decisive evidence only when removing it
would change the classification. Keep unsupported classifications `UNKNOWN`;
for unresolved risk, use the higher plausible tier as the rubric specifies.
Done when each classification has an explicit basis and a robust action, if
present, is named and supported. Use [examples.md](references/examples.md) to
resolve the documented distinctions.

### 3. Validate and decide

Resolve `<skill-dir>` to this skill's actual directory; do not depend on the
current working directory. With Python 3.10 or later, pass one object on stdin:

```bash
python3 -B "<skill-dir>/scripts/guard_decision.py" < guard-input.json
```

`INPUT_VALIDATION_ERROR` means the closed input structure is invalid.
`SEMANTIC_CONSISTENCY_ERROR` means a classification lacks a required decisive
evidence kind or contradicts the external-verification classification.
Both exit with code 2 and write JSON to stderr; neither produces a decision.
Correct inputs using supplied evidence, or report the gap. Never invent evidence
or weaken validation to obtain a result. The check verifies evidence kinds,
not whether the text is true, current, or actually supports the classification.
If Python is unavailable, manually apply both validation stages and the ordered
rules in the decision model; label the result as manual and unverified by the helper.
Done when validation succeeds and a decision is produced, or an error is reported.

### 4. Report for review

Return `guard_verdict`, `memory_action`, `memory_state`, `resolution_source`,
`decisive_evidence`, `reason_code`, `next_step`, and `boundary` without changing
the helper's result. Report validation failures separately. `PASS` concerns only
memory reliance; a high-risk underlying task still needs human review.
Done when the result and its evidence can be inspected without executing an action.

## Boundaries

Use only supplied information. Do not retrieve memories, browse, call APIs,
read credentials or private gold, modify the original response, or execute tasks.
Read [research-boundaries.md](references/research-boundaries.md) before reporting
metrics, discussing deployment, or making capability claims. This is decision
support only, not production validated. High-risk actions require human review.
