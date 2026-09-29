# P2 operational pilot: v1.1.0

Date: September 29, 2026. Stage: `operational-pilot-v2`.

Eight public cases completed under both conditions: **16 generation calls**.
All sixteen outputs passed JSON structure, source-record preservation, and helper
consistency checks. There were no incomplete outputs, semantic failures, repair
calls, or automatic retries in this generation pilot. These checks do not prove
correct classification.

The conditions used OpenAI `gpt-5.6-terra`, reasoning `medium`, the same 4,096-token
output allowance (including reasoning), JSON format, proposed USE, and public scene.
The treatment added only the classification rubric. Cases were selected before
calls by SHA-256 ordering with seed `skill-p2-v1.1.0-order:`; condition order
alternated. This small deterministic pilot is not a representative 128-case study.

## Operational results

| Measure | Contract only | With rubric |
| --- | ---: | ---: |
| Completed outputs | 8/8 | 8/8 |
| Source and helper validation | 8/8 | 8/8 |
| Incomplete or invalid outputs | 0/8 | 0/8 |

| Field | Pairs with different classifications |
| --- | ---: |
| Permission | 2/8 |
| Relationship | 3/8 |
| Evidence status | 0/8 |
| Action risk | 2/8 |
| Robust action availability | 5/8 |
| Final memory reliance | 3/8 |

Disagreement is not improvement or regression. Robust action feasibility,
current permission, scope, and action-risk interpretation need independent review.
No field accuracy, final-action accuracy, trigger precision/recall, or production
validation is reported. A direct API extraction test is not real-host skill activation.

## Usage and spending

Provider-reported usage: 41,668 input tokens and
17,441 output tokens, including 11,928
reasoning tokens. Conservative accounting totals **USD 0.3134620**,
or **CAD 0.564231600** using a 1.80 CAD/USD bound. This is an
accounting upper estimate, not an invoice or a confirmed credit-card charge.

Each generation was preceded by provider input counting and a persisted maximum
cost reservation; completed usage settled that reservation. Rates were verified
against [official pricing](https://developers.openai.com/api/docs/pricing): input
was conservatively charged at the cache-write rate of USD 2.50 per million, output
at USD 12 per million, without cache discounts. [Output limits include reasoning](https://developers.openai.com/api/docs/guides/reasoning).
The September 29 [Bank of Canada reference](https://www.bankofcanada.ca/valet/observations/FXUSDCAD/json?recent=1)
was 1.4188 CAD/USD; 1.80 provides currency/fee headroom. The runner used a USD 2.50
ceiling, below the owner's CAD 5 ceiling under that bound. Future stages must carry
forward the current ledger, reverify pricing/FX, and stop on unsettled usage.

## Provenance and separation

- Public source SHA-256: `e4c1ff0319f71925461ff6c5d6c66da73c1c5da5160d6b86449a0ffa95109d39`.
- Frozen paired-plan fingerprint: `9afc56256abfc1514e89e1ad9795d919730402bcadb46222e1953c8626184adb`.
- Helper fingerprint: `5873ccb197a6fb19b25a82de98471ad2cc64347b6fcb6a39bb7b8eefd3d772cd`.
- Historical source, gold, and STOP_AT_V07 records are unchanged.
- Public inputs, provider outputs, validated outputs, and evaluator drafts use separate local paths.
- No evaluator targets, rationales, private mappings, or review records entered model requests.
- The earlier `operational-pilot-v1` stopped on a JSON-format input-count request error before reserving or sending a generation call. Its record and the original plan were preserved. A separately inspected parameter correction produced a new plan and run directory. Two unsuccessful diagnostic token-count requests and sixteen successful token counts were separate from the sixteen generation calls.

## Next human step

Eight assistant annotation proposals were prepared from public evidence before
experimental answers were inspected. All remain DRAFT and are labeled NOT GOLD.
The offline page prioritizes those eight cases, keeps the remaining 120 blank,
and omits experimental answers and condition identities. The owner can review,
correct, and export those eight cases before a separately scoped accuracy report.
The proposals were not used to score this pilot. No further paid execution is
scheduled or automatically resumed while review is pending.
