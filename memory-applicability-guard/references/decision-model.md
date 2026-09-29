# Decision model

Use explicit structured inputs classified with [the rubric](classification-rubric.md).
The helper does not infer relationships from unrestricted prose.

## Closed input contract

Required fields:

- `current_task` and `candidate_memory`: non-empty strings.
- `proposed_memory_action`: `USE | IGNORE | ASK`.
- `permission`: `ALLOWED | REVOKED | UNKNOWN`.
- `relationship`: `DIRECT | EXPLICIT_TRANSFER | NO_BRIDGE | SUPERSEDED | CONFLICTING | UNKNOWN`.
- `evidence_status`: `SUFFICIENT | USER_RESOLVABLE | EXTERNAL_REQUIRED | UNKNOWN`.
- `robust_action_available`: boolean.
- `risk`: `LOW | MEDIUM | HIGH`.
- `evidence`: non-empty array of exact `{id, text, kind, decisive}` objects;
  IDs must be unique, ID/text non-empty strings, and decisive a boolean.

`robust_action` must be a non-empty string when robust action is available;
otherwise it must be absent or null. Evidence kinds are `MEMORY_SOURCE`,
`APPLICABILITY`, `PERMISSION`, `CURRENT_EXTERNAL`, and `USER_STATEMENT`.
A `MEMORY_SOURCE` entry cannot be decisive. Unknown fields are rejected.

## Consistency validation

Structural validation runs first. Then `validate_consistency()` checks the
requirements below, including classifications on lower-priority branches.
All missing support violations are reported together. No decision is emitted
on failure; the caller must correct the classification or report missing evidence.

| Classification | Required decisive evidence kinds |
| --- | --- |
| `permission=REVOKED` | `PERMISSION` or `USER_STATEMENT` |
| `relationship=DIRECT` | `APPLICABILITY` or `USER_STATEMENT` |
| `relationship=EXPLICIT_TRANSFER` | `APPLICABILITY` or `USER_STATEMENT` |
| `relationship=SUPERSEDED` | `APPLICABILITY`, `USER_STATEMENT`, or `CURRENT_EXTERNAL` |
| `evidence_status=EXTERNAL_REQUIRED` | Must not contain decisive `CURRENT_EXTERNAL` for the audited claim |

The requirements are centralized in `CLAIM_SUPPORT`; external-verification
consistency has its own negative check. They inspect evidence kinds and flags,
not truth, content entailment, recency, or authority. Passing is necessary for
the specified classifications, but cannot establish semantic correctness.

The CLI writes JSON errors to stderr and exits 2: `INPUT_VALIDATION_ERROR`
for invalid structure, `SEMANTIC_CONSISTENCY_ERROR` for unsupported or
incompatible classifications. Successful output remains the eight-field object.

## Ordered rules

| Priority | Condition | Verdict | State / action | Reason for precedence |
| ---: | --- | --- | --- | --- |
| 1 | Permission revoked | `PASS` or `REVISE` | `CLEAR_INAPPLICABLE / IGNORE` | Withdrawal prevents reliance regardless of relevance; high-risk underlying tasks still need human review. |
| 2 | High risk | `ESCALATE` | `UNCERTAIN / IGNORE` | A memory audit cannot approve a high-risk action. |
| 3 | External facts required | `VERIFY_EXTERNAL` | `UNCERTAIN / IGNORE` | Users should not be asked to guess current external facts. |
| 4 | No affirmative bridge | `PASS` or `REVISE` | `CLEAR_INAPPLICABLE / IGNORE` | Similarity does not establish transfer. |
| 5 | Superseded memory | `PASS` or `REVISE` | `CLEAR_INAPPLICABLE / IGNORE` | Newer controlling evidence replaces the old memory. |
| 6 | Medium risk without decisive permission/user confirmation | `ASK_USER` | `UNCERTAIN / ASK` | Consequential reliance requires explicit confirmation; reason `MEDIUM_RISK_CONFIRMATION_REQUIRED`. |
| 7 | Direct/explicit transfer + allowed + sufficient | `PASS` or `REVISE` | `CLEAR_APPLICABLE / USE` | Supported scope and permission permit reliance. |
| 8 | Conflicting evidence without robust action | `ASK_USER` | `UNCERTAIN / ASK` | Resolve competing evidence explicitly; reason `CONFLICTING_EVIDENCE`. |
| 9 | User-resolvable and no robust action | `ASK_USER` | `UNCERTAIN / ASK` | Ask only for information that changes the action. |
| 10 | Robust action available | `PASS` or `REVISE` | `UNCERTAIN / IGNORE` | A supplied robust option avoids disputed reliance and unnecessary interruption. |
| 11 | Other evidence gap | `ASK_USER` | `UNCERTAIN / ASK` | Missing applicability or permission never defaults to USE. |

## Output interpretation and compatibility

`PASS` and `REVISE` express alignment with proposed memory reliance on the
branches that use them. `ASK_USER`, `VERIFY_EXTERNAL`, and `ESCALATE` express
the required next step even when the proposed memory action already matches.
In particular, proposed ASK plus recommended ASK still yields `ASK_USER`.
The combined verdict field is retained for compatibility; a split is deferred.

`DIRECT + SUFFICIENT + permission=UNKNOWN` still yields `ASK_USER` unless a
higher-priority rule or supplied robust action applies. User-saved memories
are not implicitly marked ALLOWED. Any relaxation requires a separate decision.

Neither PASS nor REVISE approves the underlying task. REVOKED plus HIGH can
still be PASS when proposed reliance is IGNORE; the next step explicitly
retains qualified human review for the high-risk task. High-risk escalation
and external verification are recommendations only; the helper executes neither.

## Semantic separations

Relevance is not applicability; provenance is not current scope; truth is not
permission; evidence IDs do not prove correct evidence use; similarity is not
explicit transfer. Uncertainty may call for a robust action, external evidence,
or human review instead of a user question. See [research boundaries](research-boundaries.md).
