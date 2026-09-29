# P2 evaluation protocol: preparation only

Protocol version: `skill-p2-v1.1.0`. No model-generation results are reported.
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
preparation artifacts live in private Git metadata and are not published.

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

## Current preparation status

- Credential access check: authenticated access to the requested model succeeded.
- Local credential launcher: child-process environment check passed; no key stored.
- Public source: hash and 128-row count confirmed.
- Prepared: 30 synthetic trigger prompts, separate proposed route labels, and
  128 unannotated evaluator-only target rows.
- Offline preparation preflight: passed; it made zero model requests.
- Pending: accepted targets, instrumented real host, enforceable spend ceiling,
  generation calls, paired scoring, and final evaluation report.
