# Decision model

Use only explicit structured inputs. The helper does not infer relationships from unrestricted prose.

## Closed input contract

Required top-level fields:

- `current_task`: non-empty string.
- `candidate_memory`: non-empty string.
- `proposed_memory_action`: `USE | IGNORE | ASK`.
- `permission`: `ALLOWED | REVOKED | UNKNOWN`.
- `relationship`: `DIRECT | EXPLICIT_TRANSFER | NO_BRIDGE | SUPERSEDED | CONFLICTING | UNKNOWN`.
- `evidence_status`: `SUFFICIENT | USER_RESOLVABLE | EXTERNAL_REQUIRED | UNKNOWN`.
- `robust_action_available`: boolean.
- `risk`: `LOW | MEDIUM | HIGH`.
- `evidence`: non-empty array of exact `{id, text, kind, decisive}` objects.

Optional `robust_action` is required when robust action is available. Evidence kind is `MEMORY_SOURCE | APPLICABILITY | PERMISSION | CURRENT_EXTERNAL | USER_STATEMENT`. A `MEMORY_SOURCE` entry cannot be decisive applicability evidence.

## Precedence

| Priority | Condition | Verdict | State / action | Resolution |
|---:|---|---|---|---|
| 1 | Permission revoked | `PASS` or `REVISE` | `CLEAR_INAPPLICABLE / IGNORE` | User permission evidence |
| 2 | High risk | `ESCALATE` | `UNCERTAIN / IGNORE` | Qualified human review |
| 3 | External facts required | `VERIFY_EXTERNAL` | `UNCERTAIN / IGNORE` | Current external evidence |
| 4 | No affirmative bridge | `PASS` or `REVISE` | `CLEAR_INAPPLICABLE / IGNORE` | Supplied boundary evidence |
| 5 | Superseded memory | `PASS` or `REVISE` | `CLEAR_INAPPLICABLE / IGNORE` | Newer supplied evidence |
| 6 | Direct/explicit transfer + allowed + sufficient | `PASS` or `REVISE` | `CLEAR_APPLICABLE / USE` | Supplied applicability evidence |
| 7 | User-resolvable and no robust action | `ASK_USER` | `UNCERTAIN / ASK` | User |
| 8 | Robust action available | `PASS` or `REVISE` | `UNCERTAIN / IGNORE` | None needed |
| 9 | Other evidence gap | `ASK_USER` | `UNCERTAIN / ASK` | User-supplied applicability information |

`PASS` means the proposed memory action matches the deterministic recommendation; it never approves or executes the underlying task. `REVISE` recommends changing only the memory reliance decision.

## Semantic separations

- Relevance does not prove applicability.
- Provenance identifies where memory came from; it does not establish current scope.
- Truth does not grant permission.
- Citing an evidence ID does not prove correct evidence use.
- Similarity does not establish explicit transfer.
- Uncertainty does not always require ASK: use external verification, robust action, or human escalation when appropriate.
