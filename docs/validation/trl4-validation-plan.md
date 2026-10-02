# TRL4 Validation Plan

**Status:** planned  
**Date:** 2026-10-02

## 1. TRL4 target

The working objective is to move the integrated Hubstry Security research prototype from approximately TRL3 evidence toward TRL4 by validating critical components together in a controlled laboratory environment.

TRL terminology here is used as a project-planning framework; the final TRL claim should be tied to documented evidence and the applicable assessment method.

## 2. Current evidence baseline

The repository currently contains:

- HALE mathematical framework and proof-of-concept material;
- HSL research prototype;
- quantum encoding experiments and tests;
- PR1 documentation and audit status;
- an approved PR2 PQC integration specification;
- threat-model and attack-vector documentation.

These artifacts establish research and prototype evidence. They do not by themselves establish laboratory validation.

## 3. Required evidence for the next gate

### A. Real cryptographic integration

Implement and test the authorized PR2 algorithms through the provider boundary:

- ML-KEM-768;
- ML-DSA-65;
- SLH-DSA-SHA2-128s;
- HKDF-SHA-256 key schedule;
- canonical transcript.

### B. Integrated protocol behavior

Demonstrate end-to-end operation under normal and negative paths, with reproducible configuration.

### C. Laboratory scenarios

At minimum, exercise:

1. normal handshake;
2. MITM attempt;
3. transcript tampering;
4. ciphertext tampering;
5. downgrade attempt;
6. replay;
7. signature tampering;
8. context substitution.

### D. Measurements

Capture latency, throughput, message sizes, memory/CPU use, failure behavior and provider-specific metrics where applicable.

### E. Reproducibility

Retain environment manifests, dependency versions, source revision, experiment configuration and machine-readable results.

### F. Independent challenge

Subject the integrated system to adversarial testing or an independent laboratory review before treating the evidence as mature validation.

## 4. Evidence ledger

Each experiment should map:

claim → test → environment → result → artifact hash → reviewer

No claim should be upgraded from HYPOTHESIS to OBSERVED merely because implementation exists.

## 5. Suggested gate sequence

**Gate 1 — PR2 correctness:** primitive/provider tests green.

**Gate 2 — protocol integration:** handshake and negative paths green.

**Gate 3 — digital twin:** scenario matrix and evidence package reproducible.

**Gate 4 — laboratory validation:** controlled environment and adversarial testing.

**Gate 5 — TRL assessment:** evidence reviewed and documented.

## 6. NVIDIA / acceleration boundary

NVIDIA acceleration is deliberately downstream of the CPU baseline.

~~~text
PQCProvider
  ├── CPU adapter / liboqs
  └── future GPU adapter / cuPQC
          ↓
      same protocol
      same twin
      same tests
~~~

The GPU work should answer an engineering question—whether acceleration changes measurable performance characteristics—without changing the protocol semantics.

## 7. Out of scope for this gate

QPU execution, CUDA-Q research experiments, cuPQC integration, TLS/DTLS, SDR, spectral encryption and rho3 remain separate research tracks.
