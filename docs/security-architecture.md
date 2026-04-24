# Security Architecture - Hubstry Security Platform
# ==================================================
# Comprehensive security architecture document referencing both
# foundational research papers from the Hubstry Deep Tech program.
#
# Papers:
#   Paper 2 (CC BY 4.0): DOI 10.5281/zenodo.18776462
#     - pi*sqrt(f(A)) + Quantum
#     - Quantum bound on rho_3, 64-profile lattice
#
#   Paper 4 (CC BY 4.0): DOI 10.5281/zenodo.19056387
#     - HPG 1.0
#     - HSL phase-based auth, intrusion detection, LFSR key rotation
#
# Author: Hubstry Deep Tech (guilhermemachado.ceo@hubstry.dev)
# ==================================================================

## 1. Architecture Overview

The Hubstry Security Platform implements a dual-layer security architecture:

```
+---------------------------------------------------------------+
|                   Application Layer                             |
|   (APIs, Services, Business Logic)                             |
+---------------------------------------------------------------+
                            |
+---------------------------------------------------------------+
|              Security Orchestration Layer                      |
|   (Policy Engine, Audit, Compliance)                           |
+---------------------------------------------------------------+
              |                           |
+-------------------------+  +----------------------------+
|  HSL Authentication     |  |  Post-Quantum Layer        |
|  Layer                  |  |                            |
|                         |  |  +-----------+------------+|
|  +--------------------+ |  |  | rho_3     | Profile    ||
|  | H-Challenge/       | |  |  | Bound     | Lattice    ||
|  | Response Protocol  | |  |  | Analyzer  | (64-profs) ||
|  +--------------------+ |  |  +-----------+------------+|
|  +--------------------+ |  |  +------------------------+|
|  | Intrusion          | |  |  | Consistency             ||
|  | Detection          | |  |  | Projection  P_C         ||
|  | (Delta_phi>eps)    | |  |  | (7/64 consistent)       ||
|  +--------------------+ |  |  +------------------------+|
|  +--------------------+ |  |  +------------------------+|
|  | LFSR Key Rotation  | |  |  | Entanglement            ||
|  | (sigma_{k+1}=f)    | |  |  | Measures                 ||
|  +--------------------+ |  |  +------------------------+|
+-------------------------+  +----------------------------+
              |                           |
+---------------------------------------------------------------+
|              HALE Core (Mathematical Engine)                   |
|   f0 -> phi(b) -> Key Hierarchy -> Spectral Segmentation     |
+---------------------------------------------------------------+
```

## 2. HSL Authentication Layer

### 2.1 H-Challenge/Response Protocol (Paper 4)

The 3-step protocol establishes mutual authentication using phase-encoded
challenges derived from harmonic frequency subdivisions:

| Step | Direction | Content | Size |
|------|-----------|---------|------|
| 1. Challenge | Alice -> Bob | H_Challenge(phase_A, nonce_A, t_A) | ~48 B |
| 2. Response | Bob -> Alice | H_Response(phase_B, sigma_A_B, nonce_B) | ~48 B |
| 3. Verify | Alice -> Bob | H_Verify(token_AB, sign_A, session_id) | ~104 B |
| **Total** | | | **~200 B** |

**Security properties:**
- **Replay protection:** Nonce (32 bytes) + timestamp (60s window)
- **Phase coherence:** Mutual proof of shared f0 knowledge
- **Quantum resistance:** Composable with ML-DSA-65 (FIPS 204)
- **Forward secrecy:** Ephemeral harmonic phases per session

Reference: `hsl/hsl_module.py`

### 2.2 Intrusion Detection (Paper 4)

Continuous monitoring using the phase deviation criterion:

```
Delta_phi(t) = |phi_hat(t) - phi_ref| > epsilon
```

- **Threshold epsilon:** Configurable per deployment (default: 0.05 rad)
- **Sliding window:** 64 observations with adaptive thresholding
- **Alert severity:** LOW / MEDIUM / HIGH / CRITICAL based on deviation magnitude
- **Adaptive mode:** epsilon_adaptive = mean + k * std (k=3 default)

Reference: `hsl/intrusion_detection.py`

### 2.3 LFSR Key Rotation (Paper 4)

Cryptographic key rotation using a configurable LFSR:

```
sigma_{k+1} = f_LFSR(sigma_k, seed)
seed = SHA-256(str(f0) || timestamp_ns)
```

- **Register size:** 32 bits (period: 2^32 - 1 for maximal polynomial)
- **Feedback polynomial:** Configurable taps [16, 14, 13, 11]
- **Seed entropy:** f0 (shared secret) + nanosecond timestamp
- **Key derivation:** SHA-256 expansion of register state

Reference: `hsl/lfsr_key_rotation.py`

## 3. Post-Quantum Layer

### 3.1 Quantum Significance Bound (Paper 2)

The fundamental bound constraining adversarial distinguishability:

```
f_rho3(|psi>, |phi>) <= |<psi|phi>|^2
```

- **Fidelity:** |<psi|phi>|^2 measures state overlap
- **Trace distance:** T = sqrt(1 - F) quantifies distinguishability
- **Security classification:** HIGH (F > 0.95), MEDIUM (> 0.80), LOW (> 0.50), NONE

Reference: `post-quantum/rho3_bound.py`

### 3.2 64-Profile Boolean Lattice (Paper 2)

The complete lattice L = {0,1}^6 with 64 profiles isomorphic to the
6-qubit computational basis:

```
Total profiles:     64 (= 2^6)
Consistent:          7 ({000000, 000001, 000010, 000100, 001000, 010000, 100000})
Inconsistent:       57
Consistency ratio:  7/64 = 0.1094
```

Lattice operations:
- **Meet (AND):** p AND q = bitwise AND
- **Join (OR):** p OR q = bitwise OR
- **Partial order:** p <= q iff p & q == p

Reference: `post-quantum/profile_lattice.py`

### 3.3 Consistency Projection (Paper 2)

The projection operator maps any state onto the consistent subspace:

```
P_C = sum_{sigma in Sigma_C} |sigma><sigma|
```

where Sigma_C = {0, 1, 2, 4, 8, 16, 32} (7 consistent profiles).

**Entanglement measures:**
- **Von Neumann entropy:** S(rho) = -Tr(rho * log2(rho))
- **Purity:** Tr(rho^2)
- **Linear entropy:** S_L = 1 - Tr(rho^2)
- **Concurrence:** Entanglement for bipartite partitions

Reference: `post-quantum/quantum_profiles.py`

## 4. Integration Architecture

### 4.1 HSL + Post-Quantum Composition

```
Authentication Flow:
  1. HSL H-Challenge/Response (phase coherence)
  2. Consistency projection check (P_C verification)
  3. rho_3 bound verification (quantum distinguishability)
  4. ML-DSA-65 signature (FIPS 204 post-quantum binding)
  5. LFSR key rotation (session key derivation)
```

### 4.2 Threat Model

| Threat | HSL Defense | PQ Defense |
|--------|-------------|------------|
| Quantum brute force | N/A | rho_3 bound limits info leakage |
| Replay attack | Nonce + timestamp | N/A |
| Phase spoofing | Intrusion detection | Consistency projection |
| Key compromise | LFSR rotation | PQC key encapsulation |
| MITM | Mutual auth (3-step) | rho_3 + ML-DSA-65 |

### 4.3 Compliance Mapping

| Standard | HSL Component | PQ Component |
|----------|---------------|--------------|
| NIST FIPS 203 (ML-KEM) | Session key via LFSR | Key encapsulation |
| NIST FIPS 204 (ML-DSA) | Sign step (Verify) | Digital signatures |
| NIST FIPS 205 (SLH-DSA) | Backup scheme | Hash-based signatures |
| NIS2 Art. 21(2)(i) | Mutual authentication | PQC authentication |

## 5. Security Parameters

### 5.1 Default Configuration

| Parameter | Value | Source |
|-----------|-------|--------|
| f0 | 440 Hz | HALE framework |
| Base (b) | 12 | Euler totient hierarchy |
| Epsilon (intrusion) | 0.05 rad | Paper 4 |
| LFSR register | 32 bits | Paper 4 |
| LFSR taps | [16, 14, 13, 11] | Paper 4 |
| Consistent profiles | 7 of 64 | Paper 2 |
| rho_3 bound | F <= 1.0 | Paper 2 |
| HSL handshake | ~200 bytes | Paper 4 |

### 5.2 NIST Security Levels

| Level | Classical | Post-Quantum | Hubstry Mapping |
|-------|-----------|--------------|-----------------|
| 1 | AES-128 | ML-KEM-512 | IoT sensors |
| 3 | AES-192 | ML-KEM-768 + ML-DSA-65 | Default |
| 5 | AES-256 | ML-KEM-1024 + ML-DSA-87 | Critical infra |

## 6. Research References

1. **Paper 2 (CC BY 4.0):** DOI 10.5281/zenodo.18776462
   Machado, G. G. - pi*sqrt(f(A)) + Quantum: Quantum bound on rho_3,
   64-profile lattice, consistency projection.

2. **Paper 4 (CC BY 4.0):** DOI 10.5281/zenodo.19056387
   Machado, G. G. - HPG 1.0: HSL phase-based authentication,
   intrusion detection, LFSR key rotation.

3. NIST FIPS 203 - Module-Lattice-Based Key-Encapsulation Mechanism (2024)
4. NIST FIPS 204 - Module-Lattice-Based Digital Signature Standard (2024)
5. NIST FIPS 205 - Stateless Hash-Based Digital Signature Standard (2024)

---

*Hubstry Deep Tech - Security Architecture Document*
*Last updated: 2025 | License: CC BY-NC-SA 4.0*