# Post-Quantum Cryptography

## [PT-BR] Módulo de Criptografia Pós-Quântica | [EN] Post-Quantum Cryptography Module

---

## Visão Geral / Overview

Este módulo contém um provedor experimental dos padrões **NIST Post-Quantum Cryptography**, implementado sobre a biblioteca liboqs. O framework **HALE** (Harmonic Addressing & Labeling Equation) da Hubstry entra apenas como contexto de transcript e separação de domínio (ver fronteira G4 abaixo); não é fonte de chaves nem de entropia.

This module contains an experimental provider of **NIST Post-Quantum Cryptography** standards built on the liboqs library. The Hubstry **HALE** (Harmonic Addressing & Labeling Equation) framework enters only as transcript context and domain separation (see boundary G4 below); it is not a source of keys or entropy.

---

## PR2 — Real PQC Provider (specification v1.2) · Status: implemented, merged into `main` (2026-10-05)

**[IMPLEMENTED — reviewed by Luna (approve, no blockers) and merged by the PI via PR #5]** Files:

| File | Purpose |
|------|---------|
| `pqc_provider.py` | Crypto-agile `PQCProvider` facade (gate G1): registry, validation, key lifecycle, HKDF-SHA-256 key schedule with normative length-prefixed `info` encoding, canonical transcript (G3) |
| `oqs_adapter.py` | Thin liboqs adapter — implementation detail, backend-name mapping isolated here (identifier ≠ backend version ≠ library version) |
| `bench_pqc.py` | CPU benchmark with full environment/provenance metadata (G7) |
| `../tests/pqc/test_provider.py` | Test suite T0–T10 |

**Active algorithms (PR2 scope — exactly three).** "Standardized" is a property of the NIST standard; "implemented", "exercised by tests" and "integrated" are properties of this project.

| Algoritmo / Algorithm | Padrão / Standard | Status no projeto / Status in project | Exercitado por / Exercised by | Não coberto / Not covered |
|---|---|---|---|---|
| ML-KEM-768 | FIPS 203 (externo / external) | Implementado, exercitado, na `main` / implemented, exercised, on `main` | T0, T1, T4, T5, T7, T10 | — |
| ML-DSA-65 | FIPS 204 (externo / external) | Implementado, exercitado, na `main` / implemented, exercised, on `main` | T0, T2, T3, T4, T5, T7 | — |
| SLH-DSA-SHA2-128s | FIPS 205 (externo / external) | Implementado, exercitado, na `main` / implemented, exercised, on `main` | T0 (disponibilidade / availability), T2 (roundtrip), T7 (roundtrip + assinatura adulterada / tampered signature) | Tamanhos (T5), negativos de mensagem e chave trocada (T3), nível de protocolo (T4) / sizes, wrong-message and wrong-key negatives, protocol level |

Integração / Integration: os três estão na `main` desde o merge do PR #5 (2026-10-05); nenhum é usado por fluxos da plataforma, e nenhum está integrado ao handshake HSL (finding F-01b). / All three are on `main` since PR #5 was merged (2026-10-05); none is used by platform flows, and none is integrated into the HSL handshake (finding F-01b).

**Items from the PR #5 review (non-blocking):** (1) addressed in the CI PR: with `HUBSTRY_REQUIRE_PQC=1` an unavailable liboqs backend fails the PQC suite; (2) addressed in the CI PR: `_assert_sizes()` raises `BackendSizeMismatchError`; (3) open: the future HSL integration must apply `derive_session_key()` only to a canonical, versioned transcript, never to arbitrary caller-supplied bytes.

ML-KEM-512/1024 are valid FIPS 203 parameter sets but are **out of PR2 scope** (re-adding requires explicit test-matrix coverage or a new specification cycle). FN-DSA: watchlist, **blocked**. HQC: NIST-selected (not yet standardized), watchlist.

**Normative architecture (the only current one):**

```text
ML-KEM-768 (liboqs, OS/liboqs RNG)
   ↓
shared secret (candidate — FIPS 203 implicit rejection)
   ↓
HKDF-SHA-256
   ↑
salt  = SHA-256(canonical transcript)   ← full-transcript binding (T10)
info  = domain-separated, length-prefixed labels (frozen, spec v1.2 §6.1)
   ↓
session key

ML-DSA-65 / SLH-DSA-SHA2-128s → transcript authentication
```

**Sandbox validation (historical evidence, 2026-10, liboqs 0.16.0, original environment):** tests T0–T10 passing, incl. RFC 5869 HKDF vectors, info-encoding injectivity, and full-transcript session-key binding. CPU baseline (sandbox VM): ML-KEM-768 ops ≈ 0.05 ms median; ML-DSA-65 sign ≈ 0.21 ms; SLH-DSA-SHA2-128s sign ≈ 1.8 s (documented as slow; agility alternative, not default). No security-level inference from timings.

**Independent reproduction (2026-10-05):** 19/19 tests passing against liboqs 0.16.0 built from the official source (tag `0.16.0`), on this branch updated over `main` `e0055b6`. CPU medians in that environment (2 cores, x86_64): ML-KEM-768 ops ≈ 0.02 ms; ML-DSA-65 sign ≈ 0.14 ms; SLH-DSA-SHA2-128s sign ≈ 0.54 s. Timings depend on the environment and differ from the historical run; no security or performance inference. Report: [`docs/research/pr5-pqc-reproduction-report-2026-10.md`](../docs/research/pr5-pqc-reproduction-report-2026-10.md).

**Backend naming:** liboqs 0.16.0 registers SLH-DSA-SHA2-128s as `SLH_DSA_PURE_SHA2_128S`. The mapping lives only in `oqs_adapter.py`; a manual availability check using the standard name returns a false negative.

**Relation to HSL:** HSL Auth v1 (`hsl/hsl_auth_v1.py`) does not use this provider. Integrating an ML-DSA signature into the HSL handshake (audit finding F-01) is future work and requires its own specification and tests.

**T4 scope note:** T4 is a pre-Digital-Twin property test — it verifies that a tampered ciphertext breaks transcript authentication. It does **not** validate a full two-party handshake with accept/reject session rules; that validation belongs to the Digital Laboratory Twin phase.

**Architectural boundary (G4 — normative):** HALE/HSL context is transcript metadata and/or protocol-level domain-separation input; it is **not** an input to the ML-KEM primitive and is **not** cryptographic entropy.

**Scope note:** this PR provides standardized NIST algorithms through a documented liboqs backend, within the scope and limitations of this implementation. It is **not** a cryptographically validated implementation and does **not** imply whole-platform cryptographic validation.

---

## Padrões NIST de Referência / NIST Reference Standards

### FIPS 203 — ML-KEM (Module-Lattice-Based Key-Encapsulation Mechanism)

| Parâmetro | Tamanho da Chave / Key Size | Ciphertext | Security |
|-------------|---------------------------|------------|----------|
| ML-KEM-512 | 800 + 768 bytes | 768 bytes | NIST Level 1 |
| ML-KEM-768 | 1.184 + 1.088 bytes | 1.088 bytes | NIST Level 3 |
| ML-KEM-1024 | 1.568 + 1.568 bytes | 1.568 bytes | NIST Level 5 |

**PR2 status:** apenas ML-KEM-768 está ativo neste ciclo (ver escopo acima).

### FIPS 204 — ML-DSA (Module-Lattice-Based Digital Signature Algorithm)

| Parâmetro | Public Key | Signature | Security |
|-------------|-----------|-----------|----------|
| ML-DSA-44 | 1.312 bytes | 2.420 bytes | NIST Level 2 |
| ML-DSA-65 | 1.952 bytes | 3.309 bytes | NIST Level 3 |
| ML-DSA-87 | 2.592 bytes | 4.627 bytes | NIST Level 5 |

**PR2 status:** apenas ML-DSA-65 está ativo neste ciclo.

### FIPS 205 — SLH-DSA (Stateless Hash-Based Digital Signature Algorithm)

| Parâmetro | Public Key | Signature | Security |
|-------------|-----------|-----------|----------|
| SLH-DSA-128s | 32 bytes | 7.856 bytes | NIST Level 1 |
| SLH-DSA-192s | 48 bytes | 16.224 bytes | NIST Level 3 |
| SLH-DSA-256s | 64 bytes | 29.792 bytes | NIST Level 5 |

**PR2 status:** apenas SLH-DSA-SHA2-128s está ativo neste ciclo — esquema de backup sem dependência de lattice, segurança baseada unicamente em funções de hash.

---

## Legacy / Superseded Architecture — NOT normative

> ⚠️ **Historical content only.** Everything in this section describes a
> pre-PR2 placeholder design that has been **superseded** by the v1.2 key
> schedule above (HKDF-SHA-256 over the KEM shared secret, salt =
> transcript hash). Nothing here is implemented by the current provider,
> and none of it is normative. In particular, HALE-derived material is
> **not** a source of cryptographic keys or entropy.

### HALE Key Hierarchy (superseded)

```text
Level 0: f0 (fundamental frequency)
    |
Level 1: phi(b) x f0  -->  Root Key (identity)
    |
Level 2: phi(b)^2 x f0  -->  Session Keys (mutual TLS equivalent)
    |
Level 3: phi(b)^3 x f0  -->  Encryption Keys (AES-256-GCM for data)
    |
Level 4: phi(b)^4 x f0  -->  PQC Seed (input for ML-KEM key generation)
```

### Hybrid Handshake (superseded)

```text
Hybrid Handshake:
  1. X25519 (classical ECDH)       --> shared_secret_classical
  2. ML-KEM-768 (PQC KEM)          --> shared_secret_pq
  3. HALE coherence token           --> session_binding
  4. KDF = SHA-256(classical || pq || binding)
  5. AES-256-GCM with KDF-derived key
```

### Exemplo legado / Legacy example (superseded)

O código histórico em `examples/hale_mlkem.py` (arquivo não presente neste repositório; classe `HALEKeyHierarchy`,
derivação `phi(b)^level × f0 → SHA-256`) pertence ao design placeholder
anterior e **não** faz parte do provider atual. O PR2 gera chaves ML-KEM
exclusivamente via RNG do liboqs/SO.

---

## Referências | References

1. NIST FIPS 203 — Module-Lattice-Based Key-Encapsulation Mechanism Standard (2024)
2. NIST FIPS 204 — Module-Lattice-Based Digital Signature Standard (2024)
3. NIST FIPS 205 — Stateless Hash-Based Digital Signature Standard (2024)
4. RFC 5869 — HMAC-based Extract-and-Expand Key Derivation Function (HKDF)
5. NIST SP 800-227 — Recommendations for Key-Encapsulation Mechanisms
6. ENISA Post-Quantum Cryptography: Current State and Quantum Mitigation (2024)

---

*Hubstry Deep Tech — Post-Quantum Research Module*
