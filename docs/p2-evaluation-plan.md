# P2 evaluation protocol: operational pilot and later accuracy review

Protocol version: `skill-p2-v1.1.0`. The [eight-case operational pilot](p2-operational-pilot.md)
has completed; classification accuracy remains unmeasured.
This evaluation is distinct from the frozen v0.7 research experiment and
cannot reinterpret or overwrite its STOP_AT_V07 conclusion.

## Approved execution envelope

The owner approved OpenAI `gpt-5.6-terra`, reasoning `medium`, a hard ceiling
of CAD 5, and at most 318 logical generation calls: 30 real-host trigger
prompts, 128 cases under two classification conditions, and up to 32 repair
calls. No automatic transport retry, model switch, account switch, or expanded
scope is authorized. Provider pricing and a conservative USD-denominated
spend ceiling must be established before generation, including reasoning tokens.
The official [model page](https://developers.openai.com/api/docs/models/gpt-5.6-terra)
lists support for medium reasoning and Responses API; actual account access
was checked separately. Access does not establish evaluation success.

Credentials enter only the evaluation child process through environment
variables. They are excluded from repository files, requests saved to disk,
reports, and diagnostics. Keychain is not used. The local launcher and
preparation artifacts live under ignored `local/p2-v1.1.0/` and are not published.
The public offline [review workspace](../evaluation/README.md) creates blank
annotation pages from an explicitly supplied, fingerprinted public pack.

## Public sample provenance

The owner confirmed use of the v0.7 reviewed public model pack. Its SHA-256
is `e4c1ff0319f71925461ff6c5d6c66da73c1c5da5160d6b86449a0ffa95109d39`.
The current source matches the frozen reviewed-release manifest byte for byte:
128 records, each with one candidate memory. Original files are immutable.
All new annotations, calls, and results must use new versioned paths.

No private gold, mappings, rationales, twin metadata, raw historical model
outputs, or human-review records have been read or copied into model inputs.
An execution runner must recheck the source fingerprint and the public-input
allowlist before every request; a preparation check alone is insufficient.

## Execution sequence and human workload

Independent target labels are a prerequisite for accuracy claims, not for all
model generation. Start with an operational pilot using eight public cases in
both conditions. These sixteen first-pass requests are part of the existing
256-call classification allowance, not additional calls. Freeze the balanced
request plan before starting; retain incomplete and invalid results. Expand
within the approved envelope only when the pilot and budget gate permit it.

Without accepted targets, measure output completeness, structural validity,
consistency failures, observed usage, and repair behavior. Differences in these
rates do not establish better classification or safer decisions. No field or
memory-action accuracy is reported at this stage.

For later accuracy scoring, an assistant may prepare clearly marked annotation
proposals from public scenes alone. A human reviewer must confirm the targets;
model answers and helper agreement cannot independently establish their truth.
The owner need not personally write every target from scratch. Keep reviewers
blind to experimental answers and condition identities until target acceptance.
A reviewed subset can support a separately scoped report, with its selection
method and denominator disclosed; it cannot be represented as 128-case accuracy.

Human annotation is optional if the deliverable is limited to software checks
and operational error analysis. Full accuracy evaluation remains a separate
milestone. All execution still requires fingerprint/leakage checks, approved
settings, an enforceable budget, and new versioned output paths.

## Ground-truth gap

The public pack contains scenes and boundary metadata, but no accepted targets
for permission, relationship, evidence_status, risk, robust_action_available,
or decisive evidence IDs. The older public task_risk distribution is 71 high,
42 medium, and 15 low; these labels cannot automatically become targets for
the new action-risk rubric. They were produced for a different protocol.

Prepare independent evaluator-only targets under the new rubric, with review
status and source evidence IDs, before claiming field-level accuracy. Keep
annotation rationales and targets out of all model prompts. Declare acceptable
alternative evidence sets and robust options before scoring. A model's own
answer or the helper's successful validation cannot serve as ground truth.
Historical memory-action gold, if later approved for evaluator-only use, must
remain separate; document any difference between the old and new action policy.
Until targets are accepted, report only actual operational measurements such
as structural failures or consistency failures, not classification accuracy.

## Trigger evaluation

Thirty synthetic prompt proposals have been prepared: fifteen auditing
situations and fifteen exclusions covering arithmetic, translation, generic
advice, retrieval, storage, deletion, live verification, and documentation.
Expected trigger labels are separate and pending independent review. Public
prompt IDs do not encode positive/negative labels.

Use a named real agent host and record its version, model configuration,
discovery mechanism, and exposed skill catalog. Observe actual skill loading
or invocation in the host trace. A model's self-report that it would use a
skill is not host activation. A custom routing simulation must be labeled
as such and cannot substitute for this real-host measure.

The host must expose per-call usage and enforce the approved budget before
forwarding requests. Do not start a host loop whose internal calls cannot be
bounded. Isolate all non-synthetic user context and unrelated private files.
Compute precision and recall only after route labels are reviewed and actual
activation traces are collected; report undefined denominators explicitly.

## Paired classification conditions

Use the same model, reasoning, output contract, helper version, source public
case, extraction instructions, and per-call token allowance in both conditions.
The sole treatment difference is whether the classification rubric is included.
Do not compare the old and new SKILL.md wholesale and attribute all differences
to the rubric. Freeze prompt hashes and balance condition order before calls.

Each case has one candidate, so no batch mode is needed. Keep proposed reliance
consistent between conditions and document its source or fixed assignment.
Run structural validation followed by consistency validation on each extracted
input. If repair is permitted, show only the error and original public evidence;
log the first attempt separately, cap repair calls globally at 32, and do not
silently replace the primary result with a repaired answer.

## Metrics and report

Once evaluator targets are accepted, report field accuracy, decisive-ID agreement,
semantic-error rate, repair success, and final memory_action accuracy. Present
paired improved, regressed, both-correct, and both-incorrect counts per field
and for final reliance. Invalid or missing outputs remain in the denominator.
Keep first-pass and repaired results separate; disclose every uncompleted pair
and any budget stop. A partial run cannot be described as a 128-pair evaluation.

The final report must state sample counts, exact model/provider/reasoning,
prompt and source fingerprints, helper version, host, cost-accounting method,
actual usage, uncertainty, and limitations. Report no accuracy improvement until
supported by that report. A P2 result would be new evidence under this protocol,
not a replacement for the frozen v0.7 result or production validation.

## Current status

- Credential access and public source checks passed; no credential is recorded.
- The frozen v2 plan contains 128 paired public cases. Its first eight cases
  completed in sixteen generation calls; all passed source/helper validation.
- The [pilot report](p2-operational-pilot.md) records usage, conservative cost,
  condition disagreements, fingerprints, and limitations. No accuracy is claimed.
- Eight assistant target proposals remain DRAFT; they were prepared before
  experimental answer inspection and are not used as ground truth.
- Next human step: review those first eight proposals in the offline page,
  correct classifications and evidence, and export a versioned draft. The
  remaining 120 cases can wait. No further paid calls are automatically resumed.
- Later accuracy scoring requires independently accepted targets; full 128-case
  accuracy additionally requires the remaining pairs and target coverage.
- Real-host activation and reviewed route labels remain a separate pending stage.
- Future execution must carry forward the sixteen completed generation calls,
  prior costs, and all frozen fingerprints; completed calls must not be repeated.
