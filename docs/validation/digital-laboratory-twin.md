# Digital Laboratory Twin

**Status:** planned validation infrastructure  
**Date:** 2026-10-02

## 1. Objective

The Digital Laboratory Twin is a reproducible software environment for exercising Hubstry Security as an integrated protocol system before and alongside physical/laboratory validation.

It is an experimental harness, not a substitute for real-world or independent laboratory validation.

### Protocol under test — update 2026-10-05

The protocol currently intended for exercise in the Digital Laboratory Twin is **HSL Auth v1 (PSK-HMAC)** (`hsl/hsl_auth_v1.py`). The PQC provider is available on `main` but is not yet integrated into the HSL handshake (F-01b). Status of the twin is unchanged: planned.

## 2. Conceptual topology

~~~text
Node A ───── Node B
   │           │
   └── Gateway ┘
       Attacker
~~~

The twin should model endpoints, a gateway, an attacker, protocol state, cryptographic providers, timing, network faults and observability.

## 3. Layers

1. **Lab Runtime** — reproducible execution environment and dependency manifest.
2. **Protocol Twin** — Node A/Node B/gateway protocol state.
3. **Attack & Scenario Engine** — controlled faults and adversarial transformations.
4. **Observability** — structured events, timings, counters, error classes and traces.
5. **Evidence Store** — immutable experiment manifests, outputs, hashes and result summaries.

## 4. Initial scenarios

The first scenario set should include:

- normal handshake;
- man-in-the-middle attempt;
- transcript tampering;
- ciphertext tampering;
- downgrade attempt;
- replay;
- signature tampering;
- HALE/HSL context substitution.

Each scenario must state its preconditions, injected condition, expected protocol behavior, observed behavior and evidence artifact.

## 5. Evidence requirements

Each experiment should retain:

- experiment identifier;
- software revision;
- environment and dependency versions;
- protocol/provider configuration;
- input manifest;
- scenario identifier;
- timestamps;
- metrics;
- event log;
- expected result;
- observed result;
- pass/fail determination;
- hashes of retained artifacts.

## 6. Design constraint

The same functional tests should be reusable across CPU and future accelerated providers. This enables comparison without changing the protocol specification.

## 7. Boundary

The twin may establish repeatability and integration evidence. It must not be described as proof of field security, cryptographic security, quantum advantage, or physical interoperability.
