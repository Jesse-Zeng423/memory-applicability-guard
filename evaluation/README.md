# Offline annotation review

This workspace prepares independently reviewed targets for the accuracy stage of the
[P2 protocol](../docs/p2-evaluation-plan.md). Human annotation is not a prerequisite
for its earlier operational pilot and error analysis. It does not run a model, create
ground truth automatically, or authenticate a reviewer's identity.

The repository publishes the template and validator. Source packs, generated
pages, evaluator-only targets, notes, and outputs belong under ignored
`local/`. They are excluded from release inventories and checksums. Do not
commit personal memories, credentials, or evaluator-only material.

## Build a new page

Supply a public pack and its independently recorded SHA-256. The builder
requires the protocol's public field allowlist, unique case and evidence IDs,
and exactly one candidate per case. A fingerprint mismatch stops execution;
there is no override. Existing output files cannot be overwritten.

```bash
python3 -B scripts/p2_review.py build \
  --public-pack local/p2-v1.1.0/inputs/public-pack.jsonl \
  --source-sha256 e4c1ff0319f71925461ff6c5d6c66da73c1c5da5160d6b86449a0ffa95109d39 \
  --output local/p2-v1.1.0/review/annotation-v1.html
```

Open the generated HTML file in a browser. It works offline, makes no network
requests, and stores no browser-persistent state. All classification targets
start blank. Read the [classification rubric](../memory-applicability-guard/references/classification-rubric.md)
alongside each source case; historical task-risk labels are contextual evidence,
not prefilled targets under this protocol. Original source text is preserved.

## Review and preserve work

1. Classify permission, relationship, evidence status, action risk, and robust
   options independently of model outputs. Choose expected memory reliance.
2. Assign evidence roles to supplied IDs and select decisive support. Record
   ambiguity and acceptable alternatives in review notes before scoring.
3. Enter a reviewer name and mark the case reviewed. Changing a classification,
   evidence role, decisive ID, or note resets that case to draft.
4. Export a JSON draft before closing the tab. Import restores a matching draft;
   source, protocol, case, and evidence mismatches are rejected.
5. Validate the exported file. Use new versioned filenames for revisions.

```bash
python3 -B scripts/p2_review.py validate \
  --public-pack local/p2-v1.1.0/inputs/public-pack.jsonl \
  --source-sha256 e4c1ff0319f71925461ff6c5d6c66da73c1c5da5160d6b86449a0ffa95109d39 \
  --targets local/p2-v1.1.0/evaluator_only/targets-v1.json \
  --require-reviewed
```

Without `--require-reviewed`, incomplete but well-formed drafts may pass and
remain unready for execution. With it, every case must record a reviewer,
timezone-bearing timestamp, complete targets, valid evidence IDs, and helper
consistency. A passing validator only establishes this contract: it cannot
prove that the human judgment is correct or independently accepted.

The page's reviewed mark is provisional. Final acceptance is a separate human
step, and helper agreement alone cannot establish ground truth. Keep all
targets and notes out of model requests. Do not claim accuracy while targets
remain unaccepted; see the P2 protocol for the remaining budget and host gates.

## Operational preparation without human labels

`scripts/p2_operational.py` builds a deterministic paired request plan from the
same fingerprinted public source. The order alternates contract-first and
rubric-first; model, reasoning, JSON format, proposed reliance, output allowance,
and public scene are held constant. The only treatment change is the rubric.
The file can be executed to create a new versioned plan directory:

```bash
python3 -B scripts/p2_operational.py \
  --public-pack local/p2-v1.1.0/inputs/public-pack.jsonl \
  --source-sha256 e4c1ff0319f71925461ff6c5d6c66da73c1c5da5160d6b86449a0ffa95109d39 \
  --output local/p2-v1.1.0/plans/classification-v1
```

Existing plan directories are never overwritten. The module also validates
provider output against the helper and checks that task text, candidate text,
evidence IDs, and serialized source records are preserved. It does not contact
an API, load credentials, read evaluator targets, or simulate real-host routing.
An owner-specific transport remains local and is not part of the installed skill.

The accounting component reserves maximum output usage before each generation,
including reasoning tokens. It settles against total provider output usage,
retains unresolved reservations, rejects changed settings, and enforces both
call and spending limits. Provider input counting and an exclusive persistent
journal must be supplied by the transport; the in-memory component alone is
not a complete budget enforcement system.

The September 29, 2026 snapshot uses conservative input accounting at USD 2.50
per million tokens (including cache-write headroom) and output at USD 12 per
million, with no cache discounts. See [official pricing](https://developers.openai.com/api/docs/pricing)
and [reasoning output limits](https://developers.openai.com/api/docs/guides/reasoning).
Reverify rates and currency headroom before a new live run. Incomplete output
can still consume input and reasoning tokens and remains in the denominator.

## Reviewing proposals

A new page can optionally embed a matching evaluator draft with `--draft`.
Validation rejects source or record mismatches before embedding. Assistant
proposals must be explicitly labeled `ASSISTANT PROPOSAL, NOT GOLD.` in notes
and remain DRAFT; the page displays their provisional status. Preparing a
proposal does not record a human review. Keep experimental answers and condition
identities hidden from the reviewer until targets are accepted.
