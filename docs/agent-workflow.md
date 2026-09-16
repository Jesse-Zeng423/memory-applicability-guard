# Using the Memory Applicability Guard in an agent workflow

Decision support only; not production validated. The helper does not retrieve memory, call tools, or rewrite an Agent's answer. It reviews one structured JSON object and recommends whether the Agent should rely on a candidate memory.

## Where it sits

```text
before: retrieve memory -> treat it as applicable -> act
after:  retrieve memory -> classify explicit fields -> run the guard -> act only on the recommendation
```

Keep `memory_action` (`USE | IGNORE | ASK`) separate from the underlying task action. `PASS` means the proposed memory action matches the helper; it never approves the task itself.

## Exact input object

Required fields:

| Field | Allowed values |
|---|---|
| `current_task` | non-empty string |
| `candidate_memory` | non-empty string |
| `proposed_memory_action` | `USE`, `IGNORE`, `ASK` |
| `permission` | `ALLOWED`, `REVOKED`, `UNKNOWN` |
| `relationship` | `DIRECT`, `EXPLICIT_TRANSFER`, `NO_BRIDGE`, `SUPERSEDED`, `CONFLICTING`, `UNKNOWN` |
| `evidence_status` | `SUFFICIENT`, `USER_RESOLVABLE`, `EXTERNAL_REQUIRED`, `UNKNOWN` |
| `robust_action_available` | boolean |
| `risk` | `LOW`, `MEDIUM`, `HIGH` |
| `evidence` | non-empty array of `{id, text, kind, decisive}` |

Optional `robust_action` is required when `robust_action_available` is true. Evidence `kind` is `MEMORY_SOURCE`, `APPLICABILITY`, `PERMISSION`, `CURRENT_EXTERNAL`, or `USER_STATEMENT`. A `MEMORY_SOURCE` entry cannot be decisive.

Machine-readable copies live in `schema/guard-input.schema.json` and `schema/examples/`.

Minimal example:

```json
{
  "current_task": "Choose where to train this week",
  "candidate_memory": "The user trained at the downtown pool",
  "proposed_memory_action": "USE",
  "permission": "ALLOWED",
  "relationship": "SUPERSEDED",
  "evidence_status": "SUFFICIENT",
  "robust_action_available": false,
  "risk": "LOW",
  "evidence": [
    {"id": "SOURCE", "text": "Old record: trained at the downtown pool", "kind": "MEMORY_SOURCE", "decisive": false},
    {"id": "MOVE", "text": "The user has moved; the old pool is no longer convenient", "kind": "USER_STATEMENT", "decisive": true}
  ]
}
```

## Before / after review

1. Extract `current_task` and `candidate_memory` from the conversation. Do not infer missing classifications from similarity or prose.
2. Record the Agent's proposed memory action before the review.
3. Fill permission, relationship, evidence status, risk, and robust-action fields only from supplied evidence. Use `UNKNOWN` when unsupported.
4. Mark current boundary evidence `decisive=true`. Leave provenance `MEMORY_SOURCE` non-decisive.
5. Run the helper:

```bash
python3 memory-applicability-guard/scripts/guard_decision.py --file guard-input.json --pretty
```

6. Show `guard_verdict`, `memory_action`, `reason_code`, `next_step`, and `boundary` to the user or operator. Do not silently edit the original answer.
7. If validation fails, correct the input using the stderr `issues` list. Do not weaken validation.

## Example agent prompt

```text
You are reviewing whether a retrieved memory should influence the next recommendation.

Do not treat relevance as applicability. Classify only explicit supplied evidence
into the Memory Applicability Guard input contract, then run the helper. Return
the helper JSON unchanged, plus one sentence that restates next_step.

If permission, relationship, or evidence_status cannot be supported, use UNKNOWN.
If risk is HIGH, do not approve the task. If evidence_status is EXTERNAL_REQUIRED,
do not ask the user to guess a live fact.
```

## Output fields and reason codes

| Output field | Meaning |
|---|---|
| `guard_verdict` | `PASS`, `REVISE`, `ASK_USER`, `VERIFY_EXTERNAL`, or `ESCALATE` |
| `memory_action` | Recommended memory reliance: `USE`, `IGNORE`, or `ASK` |
| `memory_state` | `CLEAR_APPLICABLE`, `CLEAR_INAPPLICABLE`, or `UNCERTAIN` |
| `resolution_source` | Who or what resolved the decision |
| `decisive_evidence` | Evidence items marked decisive, in input order |
| `reason_code` | Stable machine-readable why |
| `next_step` | Operator-facing instruction |
| `boundary` | Research/product boundary; keep it visible |

| Reason code | Typical meaning |
|---|---|
| `PERMISSION_REVOKED` | Ignore the memory; permission evidence wins |
| `HIGH_RISK_HUMAN_REVIEW_REQUIRED` | Escalate; do not act from memory |
| `EXTERNAL_VERIFICATION_REQUIRED` | Verify current/third-party facts; do not ask the user to guess |
| `NO_BRIDGE` | No affirmative transfer to the current task |
| `SUPERSEDED` | Newer supplied evidence replaces the memory |
| `DIRECT` / `EXPLICIT_TRANSFER` | Allowed and sufficiently evidenced use |
| `USER_RESOLVABLE_UNCERTAINTY` | Ask one action-changing question |
| `ROBUST_ACTION_AVAILABLE` | Ignore the disputed memory and take the named robust action |
| `EVIDENCE_GAP` | Ask for the missing applicability or permission fact |

`PASS` versus `REVISE` only compares the proposed memory action with the recommended one for some branches. `ASK_USER`, `VERIFY_EXTERNAL`, and `ESCALATE` are fixed verdicts.

## Research boundary

Preserve `STOP_AT_V07`. This workflow makes an auditable review explicit; it did not beat the frozen baseline and is not a production safety control. Do not use it to autonomously approve medical, legal, financial, employment, insurance, housing, privacy, or safety-critical decisions.
