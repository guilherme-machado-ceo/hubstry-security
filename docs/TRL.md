# Technology Readiness Level (TRL) Evidence Ledger

**Date:** 2026-10-02  
**Working assessment:** approximately TRL3 for the overall research prototype; TRL4 is a target gate, not a completed status.

## Evidence by level

| Level | Evidence status |
|---|---|
| TRL1 | Fundamental concepts and research questions documented. |
| TRL2 | HALE/HSL architecture and application concepts documented. |
| TRL3 | Proof-of-concept software, mathematical experiments, tests, architecture and threat-model material exist. |
| TRL4 | **Target / not yet established.** Requires integrated critical components validated in a controlled laboratory environment with repeatable evidence. |

## TRL4 evidence checklist

- [ ] Real ML-KEM-768 integration.
- [ ] Real ML-DSA-65 integration.
- [ ] Real SLH-DSA-SHA2-128s integration.
- [ ] Canonical transcript implemented and tested.
- [ ] HKDF-SHA-256 key schedule implemented and tested.
- [ ] Positive and negative protocol tests.
- [ ] Digital Laboratory Twin.
- [ ] Adversarial scenario matrix.
- [ ] Reproducible environment manifest.
- [ ] Performance and resource measurements.
- [ ] Machine-readable evidence artifacts.
- [ ] Independent or external laboratory challenge/review.

## Claim discipline

Use the following vocabulary in research records:

- **OBSERVED** — directly measured or reproduced under documented conditions.
- **DERIVED** — follows from an explicit mathematical or logical derivation.
- **LITERATURE-SUPPORTED** — supported by an identified external source.
- **HYPOTHESIS** — proposed but not yet demonstrated.
- **NOT TESTED** — no evidence collected yet.

Do not convert a roadmap milestone, implementation existence, simulation result or model inference into a higher TRL claim without corresponding evidence.

## Next assessment gate

Reassess the ledger after PR2 implementation, Digital Laboratory Twin execution and controlled/adversarial validation.
