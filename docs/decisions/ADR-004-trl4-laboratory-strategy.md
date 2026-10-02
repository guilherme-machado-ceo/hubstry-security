# ADR-004 — TRL4 Laboratory Strategy

**Status:** accepted planning decision  
**Date:** 2026-10-02

## Context

Hubstry Security has research papers, mathematical experiments, prototype code, tests and an approved PQC integration specification. The next engineering objective is integrated laboratory evidence.

A key risk is allowing acceleration, QPU experiments or speculative quantum work to obscure whether the core security protocol works correctly on a reproducible CPU baseline.

## Decision

Build the validation path in this order:

1. establish the CPU/liboqs PQC baseline;
2. integrate the canonical transcript and HKDF-SHA-256 key schedule;
3. validate positive and negative protocol behavior;
4. build the Digital Laboratory Twin and evidence package;
5. execute controlled/adversarial laboratory scenarios;
6. only then evaluate NVIDIA acceleration as a separate provider/backend;
7. keep QPU, rho3 and other speculative quantum tracks isolated from the TRL4 security-engineering gate.

## Consequences

### Positive

- preserves a clear experimental baseline;
- makes CPU/GPU comparisons scientifically meaningful;
- separates protocol correctness from acceleration;
- creates reusable evidence for later laboratory review.

### Constraints

- NVIDIA work is not part of the initial PR2 baseline;
- passing software tests does not establish field security;
- speculative quantum claims cannot be used as TRL4 evidence without separate validation.

## Related records

- docs/research/pr2-pqc-specification.md
- docs/validation/digital-laboratory-twin.md
- docs/validation/trl4-validation-plan.md
- docs/research/pr1-quantum-encoding.md
