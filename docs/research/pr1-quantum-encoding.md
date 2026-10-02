# PR1 — Quantum Encoding Comparison & 64-Profile Lattice

**Experimental record** · PR #2 merged 2026-10-03 · merge `632f680e9d3ac8e534362481d99e77cfad1fc18d`
**Branch:** `feat/pqc-real-quantum-lattice` (base `90a76aa`) · **Classification vocabulary:** OBSERVED / DERIVED / LITERATURE-SUPPORTED / HYPOTHESIS / NOT TESTED

---

## 1. Scope

Four new files, +577/−0, no existing file modified. NumPy-only. No liboqs,
no CUDA-Q, no QPU, no cloud execution. `post-quantum/rho3_bound.py`
deliberately untouched (separate audit pending).

| File | Purpose |
|------|---------|
| `quantum/encoding_compare.py` | Baseline vs equatorial encoding comparison |
| `quantum/lattice64.py` | 64 profiles encoded in a 6-qubit computational basis + consistency projector P_C |
| `tests/test_encoding.py` | Encoding tests incl. Required Change #1 |
| `tests/test_lattice64.py` | Lattice/projector tests |

## 2. Research question (approved at the review gate)

> Does the equatorial encoding eliminate the dependence of adjacent-state
> fidelity on the position k observed in the current encoding?

**Answer: yes** — proven symbolically and measured numerically.

## 3. Results

### 3.1 Encoding comparison [OBSERVED / DERIVED]

| n | current: F_min → F_max | equatorial: F (uniform) |
|---|------------------------|--------------------------|
| 4 | 0.5000 = 0.5000 (coincide) | 0.5000 |
| 8 | 0.7500 → 0.8536 | 0.8536 |
| 12 | 0.8750 → 0.9330 | 0.9330 |
| 64 | 0.9952 → 0.9976 | 0.9976 |
| 256 | 0.9997 → 0.9998 | 0.9998 |

- [DERIVED] Equatorial: `F(Δθ) = cos²(Δθ/2)` exactly — verified symbolically
  (SymPy) and numerically for **all pairs** (k,j), all n. Adjacent grid:
  `F_n = cos²(π/n)`. Translation-invariant by construction.
- [DERIVED] Current encoding: symbolic expansion shows explicit dependence on
  absolute position (terms in cos(2s), cos(2(d+s)), cos(d+2s)).
- [OBSERVED] Exact constants at n=8: F_min = 3/4, F_max = (2+√2)/4.
- [OBSERVED] Phase sensitivity to a fixed perturbation (δ=0.05 rad):
  position-independent for equatorial; position-dependent for current.
- Normalization error ≤ 2.2e-16; periodicity F(ψ(0), ψ(2π)) = 1.0, both encodings.

### 3.2 Lattice64 [OBSERVED]

- Encoded consistent profiles (7 of 64, per Paper 2): P_C = 1.0 exactly.
- Encoded inconsistent profiles: P_C = 0.0 exactly.
- Uniform superposition of one consistent + one inconsistent profile: P = 0.5.
- Consistent profile + 5% complex Gaussian noise: anomaly ≈ 0.14.
- Projector properties tested: idempotent, Hermitian, trace = 7.

### 3.3 Test suite [OBSERVED]

- **136 pytest cases** passing (cases collected by pytest, incl. parametrizations).
- Required Change #1 (review gate): `current_encoding` ≡ `harmonic_qubit`
  verified over **520 (k,n) combinations** (4+8+12+16+32+64+128+256), zero drift.
- Reproduced in 3 independent environments.

## 4. Framing decisions (from review)

1. The equatorial encoding **is the standard phase encoding** (IBM Quantum
   Learning: `P(φ)|+⟩`). Adopted as a known experimental reference — NOT a
   Hubstry contribution. The potential contribution is the follow-up question:
   what this encoding yields inside the HALE/HSL architecture for phase
   representation, comparison, anomaly detection and PQC integration.
2. **No quantum advantage or quantum security is claimed.** Fidelity ≠
   security; anomaly score ≠ cryptographic security level.
3. `2⁶ = 64` is a computational encoding, not physical qubits.

## 5. Literature limitations (deliberately sought) [LITERATURE-SUPPORTED]

- Slattery et al., Phys. Rev. A 107, 062417 (2023): numerical evidence
  against quantum advantage of fidelity kernels on classical data.
- arXiv:2503.05602 (2026): bandwidth-tuned quantum kernels converge to
  classical RBF/polynomial kernels.
- Wang et al., Quantum 5, 531 (2021): quantum-kernel advantage vanishes with
  large datasets, few measurements, high noise.

**Consequence:** Experiment E-C (anomaly detection) must ship with a
classical baseline (circular distance, RBF kernel over phase). If merit
exists, expect it in metric/engineering terms, not quantum advantage.

## 6. Not tested here [NOT TESTED]

- Any security or anomaly-detection utility (E-C).
- CUDA-Q/GPU execution, QPU execution.
- `rho3_bound.py` correctness (separate audit).

## 7. Next gates

1. `research/audit-rho3-bound` — mathematical audit (counterexample known:
   implemented inequality fails for F < (3−√5)/2 ≈ 0.382).
2. PR2 — real PQC via liboqs, only after approval.

---

*Hubstry Deep Tech — research record. This document records experiments;
it is not software documentation and asserts no validated hypothesis beyond
what is classified above.*
