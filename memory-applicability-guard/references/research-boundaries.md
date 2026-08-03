# Research and product boundaries

## Required public description

> Research-informed Memory Applicability Guard  
> Decision support only; not production validated.

This package translates frozen research concepts into a reusable structured review workflow. It does not establish a new research result or overturn the preregistered stopping decision.

## Frozen v0.7 evidence

- A0 Direct Minimal: 110/128 raw memory-action correct.
- M1 Minimal Evidence-First: 110/128 raw memory-action correct.
- Matched net improvement: 0.
- Matched transitions: M1 improved 6 cases and regressed 6 cases.
- Strict-twin stable flips: M1 27/40; A0 28/40.
- ASK recall: 60% for both conditions.
- Frozen conclusion: `STOP_AT_V07`.

These results come from a single model/reasoning setting and synthetic expert-reviewed cohorts. They do not establish cross-model, real-user, or production validity.

## Allowed claims

- The Skill turns research concepts into an auditable review process.
- It makes evidence, state, permission, resolution source, and memory-action binding explicit.
- It supports demonstrations, audits, synthetic cases, and later research.

## Forbidden claims

- It beat the matched baseline or was proved to improve accuracy.
- It is a production-grade or safety-validated Guard.
- It provides a safety guarantee.
- The project trained or fine-tuned a model.
- It may autonomously handle medical, legal, financial, employment, insurance, housing, privacy, or safety-critical decisions.

## Operational boundary

The helper uses only supplied JSON and the Python standard library. It does not retrieve memory, browse, call a model or external API, read environment credentials, access private gold, execute actions, or rewrite an Agent response. Escalate high-risk use to qualified human review.
