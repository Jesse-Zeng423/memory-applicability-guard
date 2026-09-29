# Classification rubric

Classify only supplied evidence. Evidence-kind support is necessary where the
helper requires it; it does not prove that the evidence content supports a claim.
Use this order: evidence → permission → risk → evidence_status → relationship → robust.

## Evidence kinds and decisive flags

| Kind | Use when | Positive example | Do not use when |
| --- | --- | --- | --- |
| `MEMORY_SOURCE` | Identifying the original remembered record | Earlier note: the user preferred slides | Establishing current scope or permission; never decisive |
| `APPLICABILITY` | Supplied current evidence establishes scope or transfer | Current task brief explicitly includes the earlier formatting policy | Only topic similarity or original provenance is supplied |
| `PERMISSION` | Supplied evidence explicitly permits or revokes the relevant reliance | Current consent record withdraws use of the old preference | The memory is merely true or user-authored |
| `CURRENT_EXTERNAL` | A current, already-supplied external fact has been verified for this claim | Current verified timetable replaces the remembered timetable | Verification has not occurred or the fact addresses a different claim |
| `USER_STATEMENT` | The user supplies a current boundary, permission, or preference | The user asks to reuse the prior format for this task | An agent's inference is being attributed to the user |

`decisive=true` means removing that evidence would change a classification.
Preserve supplied IDs and wording. Do not mark background facts decisive.
With redundant support, identify the minimal jointly decisive support set;
do not pretend provenance establishes applicability. Kind alone is insufficient.

## Permission

| Value | Condition | Positive example | Counterexample |
| --- | --- | --- | --- |
| `ALLOWED` | Supplied permission covers this memory and proposed reliance | Current user instruction explicitly authorizes reuse | User-authored memory without an explicit permission basis |
| `REVOKED` | Current evidence withdraws applicable permission | User says to stop using that memory | New preference replaces old content without withdrawing permission |
| `UNKNOWN` | Permission scope is absent or unresolved | Existing preference with no permission information | Explicitly revoked permission |

`REVOKED` requires decisive `PERMISSION` or `USER_STATEMENT` evidence.
User-saved memories do not receive a new implicit authorization default.

## Risk of the affected action

Assess the action influenced by memory, not whether the memory sounds harmless.
If the tier is unresolved, select the higher plausible tier and explain why.

| Value | Condition | Positive example | Counterexample |
| --- | --- | --- | --- |
| `LOW` | Easily reversible, limited consequence | Drafting workshop notes | A consequential disclosure or irreversible commitment |
| `MEDIUM` | Meaningful cost or consequence, below a high-risk domain | Selecting a paid workshop format before user confirmation | Harmless formatting; a clinical treatment decision |
| `HIGH` | Medical, legal, financial, employment, insurance, housing, privacy, or safety-critical decision | Memory affects a clinical recommendation or private-data disclosure | A reversible outline with no sensitive information |

`MEDIUM` needs decisive `PERMISSION` or `USER_STATEMENT` confirmation before USE.
This is a kind-presence requirement; callers must check the actual scope.

## Evidence status

| Value | Condition | Positive example | Counterexample |
| --- | --- | --- | --- |
| `SUFFICIENT` | Supplied evidence resolves the relevant boundary | Current instruction clearly establishes task scope | A relevant historical memory alone |
| `USER_RESOLVABLE` | A user answer would change the action, without a missing external prerequisite | Unclear choice between two formats | A live price that only a current source can establish |
| `EXTERNAL_REQUIRED` | A current or third-party fact still needs verification | Unverified current availability | Already-verified decisive external evidence for that same claim |
| `UNKNOWN` | The missing evidence and resolution source are not established | Incomplete task context | A known missing external fact |

If both user input and external facts are missing, use `EXTERNAL_REQUIRED` first.
It cannot coexist with decisive `CURRENT_EXTERNAL` for the same audited claim.
For partially verified multi-claim situations, narrow the audit to one claim and
keep other facts non-decisive; never delete valid evidence just to pass validation.

## Relationship

| Value | Condition | Positive example | Counterexample | Required decisive kinds |
| --- | --- | --- | --- | --- |
| `DIRECT` | Memory applies within the same evidenced task scope | Same workshop and still-current formatting instruction | A new workshop that only looks similar | `APPLICABILITY` or `USER_STATEMENT` |
| `EXPLICIT_TRANSFER` | Supplied evidence affirmatively carries memory into a new scope | User says to reuse the old format in the new workshop | Two similar activities without transfer evidence | `APPLICABILITY` or `USER_STATEMENT` |
| `NO_BRIDGE` | Supplied context establishes a different scope with no affirmative bridge | Personal preference proposed for a team decision without transfer | Missing context that leaves scope unknown | No additional kind requirement |
| `SUPERSEDED` | Newer applicable evidence clearly replaces the remembered rule or fact | Current format instruction replaces the old one | Two conflicting records without known order or authority | `APPLICABILITY`, `USER_STATEMENT`, or `CURRENT_EXTERNAL` |
| `CONFLICTING` | Competing evidence remains unresolved | Incompatible current directions with no clear precedence | Clearly newer controlling instruction | No additional kind requirement |
| `UNKNOWN` | Relationship cannot be established from supplied context | Task scope is missing | Explicit transfer instruction | No additional kind requirement |

Distinguish `DIRECT` from `EXPLICIT_TRANSFER` by whether the scope changes;
explicit transfer from similarity by an affirmative bridge; `NO_BRIDGE` from
`UNKNOWN` by known scope; `SUPERSEDED` from `CONFLICTING` by clear precedence;
and `SUPERSEDED` from `REVOKED` by content replacement versus permission withdrawal.

## Robust action

Set `robust_action_available=true` only for a named, feasible action acceptable
in all reasonable interpretations, with lower cost than asking. A reusable,
reversible outline may qualify when both potential formats can use it.
Inaction and asking the user do not qualify by themselves. Unknown feasibility
or an action acceptable in only one interpretation means false. Robust action
cannot bypass revoked permission, high risk, external verification, or the
medium-risk confirmation rule. The helper does not verify robustness itself.
