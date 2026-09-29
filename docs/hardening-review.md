# P0/P1 hardening and contributor PR review

Snapshot: September 29, 2026. Baseline: `e7aac2e`. Version: `1.1.0`.
The previous sandbox commits were unavailable; this implementation was rebuilt
from the supplied handoff. No historical research artifacts were modified.

## Status by evidence level

- Implemented: evidence-kind consistency checks, medium-risk confirmation,
  conflict reasoning, retained high-risk task review after revocation, and a
  classification rubric with concise skill routing.
- Tested offline: 47 tests; all original 22 tests unchanged; three existing
  example CLI outputs byte-identical to the baseline; A–G exercised through
  the absolute-path CLI from an unrelated working directory.
- Prepared offline: a blank 128-case annotation workspace with source checks,
  draft import/export, review invalidation on edits, and evaluator validation.
  Browser interaction checks passed; no reviewed targets were created.
- Verified in a real agent host: not yet established. No activation, extraction
  accuracy, or end-to-end improvement is claimed by these software checks.
- Still incomplete: P2 model evaluation and accepted field-level evaluation
  targets; all optional P3 changes. External evaluation authorization does not
  establish evaluation results. GitHub CI status is recorded in the PR checks.

The evidence-kind validator does not test evidence truth, recency, authority,
or whether text entails the classification. Missing support produces a
`SEMANTIC_CONSISTENCY_ERROR` rather than a downgraded recommendation.

## Contributor dependency chain

Read-only Git ancestry checks confirm that PR #2 is an ancestor of #3 and
#3 is an ancestor of #4. All three target `main` but were based on `321b989`,
before the MIT packaging update. Their larger file counts include earlier
PR changes, so they should not be treated as independent patches.

## Review findings

### PR #2: CLI improvements

[PR #2](https://github.com/Jesse-Zeng423/memory-applicability-guard/pull/2)
adds useful file input, formatting, schema output, and validation-only options.
Before integrating:

- `--validate-only` currently invokes only structural validation. It must
  also run `validate_consistency()` so unsupported transfer is not called VALID.
  Offline reproduction: unsupported EXPLICIT_TRANSFER returns VALID today.
- `_error_payload()` hardcodes INPUT_VALIDATION_ERROR. Preserve each error's
  `code` so semantic failures remain distinguishable.
- `collect_input_errors()` uses unguarded set membership for evidence kinds.
  Offline reproduction: an array in evidence.kind raises TypeError. Preserve
  the current type checks and malformed-type regression tests when rebasing.
- Keep version 1.1.0, the absolute skill path guidance, current English README,
  MIT scope, and current integrity generator. Do not update the historical
  v1.0.0 manifest to describe a new release.

### PR #3: schemas and synthetic contract examples

[PR #3](https://github.com/Jesse-Zeng423/memory-applicability-guard/pull/3)
adds input/output schemas and eight examples. Six examples execute under the
hardened helper; two produce semantic errors:

- `external-required.json` marks missing live information as decisive
  CURRENT_EXTERNAL. It is not a verified current external fact; reclassify
  that supplied boundary or narrow the audited claim without inventing data.
- `permission-revoked.json` combines DIRECT with only decisive PERMISSION
  evidence. Add actual scope support or revise the relationship; permission
  evidence alone does not support DIRECT under CLAIM_SUPPORT.
- The input schema permits `robust_action=null` when availability is true,
  while the helper requires a nonempty string. The true branch must constrain
  the value as well as require the field.
- Represent the new consistency requirements where JSON Schema supports them,
  and explicitly document any helper-only constraint, including unique IDs.
  Output reason codes must include MEDIUM_RISK_CONFIRMATION_REQUIRED and
  CONFLICTING_EVIDENCE; decisive MEMORY_SOURCE should remain disallowed.
- Preserve the historical manifest and regenerate only current metadata.

### PR #4: table-driven edge tests

[PR #4](https://github.com/Jesse-Zeng423/memory-applicability-guard/pull/4)
adds useful branch and validation coverage, but some fixtures assert old behavior:

- Empty decisive support with DIRECT currently expects PASS; P0 must reject it.
- A conflicting relationship currently expects EVIDENCE_GAP; use the distinct
  CONFLICTING_EVIDENCE reason when no robust alternative applies.
- Its `.issues` assertions depend on #2's exception interface. Preserve the
  semantic error subclass and its code when introducing that interface.
- The medium-risk fixture includes decisive USER_STATEMENT, so PASS remains
  valid there. Add a separate case lacking user/permission confirmation.

## Recommended integration order

Review and merge the P0/P1 hardening PR first, after its CI passes. Then rebase
and adapt #2 onto that accepted contract, followed by #3 and #4 in dependency
order. Alternatively, retarget #3 to #2's branch and #4 to #3's branch while
work is in progress, then return each to main as its dependency merges.

This is an integration recommendation, not authorization to merge or contact
the contributor. No contributor PR was merged or commented on during review.
A later review is required for the additional open PRs #5–#8.

## Research boundary

Preserve `STOP_AT_V07`: A0 and M1 both scored 110/128; matched net improvement
was zero. P0/P1 adds engineering checks and instructions. It does not prove
improved agent classification, real-world utility, or production safety.
