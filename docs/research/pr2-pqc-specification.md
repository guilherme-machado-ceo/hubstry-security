# PR2 — PQC Integration Specification v1.2

**Status:** approved specification; implementation authorized  
**Date:** 2026-10-02  
**Scope:** ML-KEM-768, ML-DSA-65, SLH-DSA-SHA2-128s; liboqs adapter; crypto-agile provider; HKDF-SHA-256; canonical transcript; T0–T10 validation.

## 1. Purpose

PR2 moves the repository from simulated/placeholder PQC claims toward an experimentally testable integration of standardized post-quantum algorithms.

This work does **not** replace the HALE/HSL research layer. HALE/HSL context is complementary metadata and domain separation material; it is not used as KEM input or entropy.

## 2. Authorized algorithms

| Function | Algorithm | Identifier |
|---|---|---|
| KEM | ML-KEM-768 | exact protocol algorithm ID defined by PR2 |
| Signature | ML-DSA-65 | exact protocol algorithm ID defined by PR2 |
| Signature | SLH-DSA-SHA2-128s | exact protocol algorithm ID defined by PR2 |

Algorithm identifiers are protocol-level identifiers and remain independent of backend/library version strings.

## 3. Provider boundary

The protocol depends on a PQCProvider facade. The liboqs implementation is an adapter behind that boundary.

The provider must expose a stable lifecycle and capability surface without leaking backend object-lifecycle assumptions into protocol code.

## 4. Key schedule

PR2 v1.2 uses HKDF-SHA-256:

- salt = transcript_hash
- IKM = shared_secret
- L = 32
- domain_separator = "hubstry-hsl/v1"
- info = domain_separator || LP(protocol_version) || LP(purpose_label) || LP(HALE_context_label) || LP(kdf_algorithm_id)
- LP(x) = uint32_be(len(x)) || x

The length-prefix encoding is part of the specification to make concatenation unambiguous and injective.

HALE/HSL context labels provide domain separation/context binding; they are not a substitute for cryptographic entropy.

## 5. Canonical transcript

The handshake transcript must have a canonical serialization. T9a–T9e cover the required transcript elements and ordering. The implementation must make the encoding deterministic and independently reproducible.

The transcript hash is used as the HKDF salt. It is not a secret.

## 6. Validation gates

- **T0:** provenance/capability evidence for the selected backend and algorithms.
- **T1–T3:** provider and primitive correctness.
- **T4:** protocol-level tampered-ciphertext acceptance property. A tampered ciphertext must not result in acceptance of the original shared secret as an authenticated session key. Implicit rejection is observed separately.
- **T5–T7:** integration, interoperability and negative-path behavior.
- **T8:** reproducibility of protocol behavior; deterministic crypto is not assumed.
- **T9a–T9e:** canonical transcript coverage.
- **T10:** RFC 5869 vectors, domain separation, and encoding injectivity.

## 7. Explicit exclusions

PR2 does not authorize:

- rho3 work;
- lattice64 changes;
- QPU/CUDA-Q experiments;
- cuPQC/NVIDIA integration;
- TLS/DTLS integration;
- SDR work;
- spectral encryption;
- secrets in source, issues, commits, logs, or chat.

## 8. Acceptance principle

Passing tests demonstrates implementation behavior under the documented test conditions. It does not by itself establish cryptographic security, quantum advantage, or regulatory compliance.

## 9. Relationship to TRL4

PR2 is one enabling workstream for laboratory validation. TRL4 evidence requires integration of critical components, documented experimental conditions, repeatable tests, negative/adversarial scenarios, measurements, and retained evidence.
