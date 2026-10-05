# Technology Readiness Level (TRL) Evidence Ledger

**Date:** 2026-10-02  
**Working assessment:** approximately TRL3 for the overall research prototype; TRL4 is a target gate, not a completed status.

## Status update — 2026-10-05

The sections below this one are the original record of 2026-10-02 and are kept unchanged. This update separates **component maturity** from **system maturity**.

### Current state

| Object | State |
|---|---|
| HALE | Research framework / proof-of-concept material |
| HSL v0 (`hsl/hsl_module.py`) | Historical record; audit findings reproducible by tests |
| HSL Auth v1 (`hsl/hsl_auth_v1.py`) | Experimental prototype, implemented and tested (PSK + HMAC-SHA-256) |
| PQC provider (`post-quantum/pqc_provider.py`) | Implemented, tested, independently reproduced, on `main` (PR #5) |
| ML-KEM-768 / ML-DSA-65 / SLH-DSA-SHA2-128s | Provider-level implementation on `main`; not used by any platform flow |
| Canonical transcript | Implemented and tested in the provider (T9a–T9e) |
| HKDF-SHA-256 key schedule | Implemented and tested (T10, RFC 5869 vector) |
| HSL + ML-DSA | Pending (finding F-01b) |
| Digital Laboratory Twin | Planned |
| Integrated adversarial validation | Pending |
| **System TRL 4** | **Not established** |

### TRL4 checklist, separated by level

**Component / provider level**

- [x] ML-KEM-768 implemented and tested through the provider boundary.
- [x] ML-DSA-65 implemented and tested through the provider boundary.
- [x] SLH-DSA-SHA2-128s implemented and tested through the provider boundary (narrower test coverage; see `post-quantum/README.md`).
- [x] HKDF-SHA-256 key schedule implemented and tested.
- [x] Canonical transcript implemented and tested.
- [x] Independent reproduction of the PQC suite.

**Protocol / system level**

- [ ] ML-DSA integrated into the HSL handshake (F-01b).
- [ ] Complete integrated handshake with positive and negative protocol tests.
- [ ] Digital Laboratory Twin.
- [ ] Integrated adversarial scenario matrix.
- [ ] Controlled laboratory validation.
- [ ] Independent or external laboratory challenge/review.

**Reproducible environment manifest:** partially established. CI (three gates: syntax, general tests, PQC with required backend) and dated reports record versions, environment and results; a system-level evidence package does not exist yet.

### TRL rule applied

Component results do not raise the system TRL. Provider-level evidence is recorded at component level only.

> **System TRL 4 for Hubstry Security: not established.**

### Evidence references

- [`research/hsl-documentation-audit-2026-10.md`](research/hsl-documentation-audit-2026-10.md)
- [`research/hsl-v1-execution-report-2026-10.md`](research/hsl-v1-execution-report-2026-10.md)
- [`research/pr5-pqc-reproduction-report-2026-10.md`](research/pr5-pqc-reproduction-report-2026-10.md)
- CI workflow: [`../.github/workflows/ci.yml`](../.github/workflows/ci.yml)

---

## Original record — 2026-10-02

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
