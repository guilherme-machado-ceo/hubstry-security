# Quantum Research Track

This directory turns the HALE/HSL harmonic hypothesis into a measurable
quantum-information experiment without claiming that the current prototype
is quantum-secure.

The first experiment maps a harmonic phase

    theta_k = 2*pi*k/n

to a normalized qubit state

    |psi(theta)> = cos(theta/2)|0> + exp(i*theta) sin(theta/2)|1>.

We measure fidelity and phase distance between states.

## Research question

The original hypothesis is that harmonic subdivision has no natural terminal
scale. That does NOT imply that the harmonic series automatically becomes
quantum.

The testable question is whether the harmonic parameterization produces
useful invariants in a quantum state space, such as distinguishability,
robustness under perturbation, collision behavior, anomaly sensitivity, and
scaling from n=12 to larger subdivisions.

## NVIDIA path

NVIDIA CUDA-Q is the preferred optional backend because Hubstry is a member
of NVIDIA Inception. CUDA-Q provides a Python programming model for hybrid
CPU/GPU/QPU workflows and GPU-accelerated quantum simulation.

Run the CPU baseline first:

    python -m quantum.harmonic_state

In an NVIDIA-capable environment:

    pip install cudaq
    python -m quantum.cudaq_probe

For larger simulations, NVIDIA cuQuantum provides GPU-accelerated
state-vector and tensor-network simulation.

## PQC path

Do not replace NIST cryptography with the harmonic construction.

Near-term architecture:

    HALE/HSL context
          |
          +---- ML-KEM (FIPS 203) ---- session key
          |
          +---- ML-DSA (FIPS 204) ---- authentication
          |
          +---- harmonic/quantum research ---- identity/segmentation signal

NVIDIA cuPQC is a later acceleration target. It provides GPU implementations
of ML-KEM and ML-DSA; first establish a correct standardized CPU baseline,
then benchmark GPU acceleration.

## Reproducibility

Record subdivision n, phase index k, fidelity, perturbation, false-accept /
false-reject behavior, CPU/GPU runtime, memory, backend and version.

No security claim should be made from simulation alone.

---

## PR1 Results (merged, PR #2, 2026-10-03)

### What was demonstrated

**Encoding comparison** (`encoding_compare.py`) — the repo baseline encoding
`cos(theta/2)|0> + e^{i*theta}sin(theta/2)|1>` was compared against the
equatorial encoding `(|0> + e^{i*theta}|1>)/sqrt(2)` for subdivisions
n = 4, 8, 12, 16, 32, 64, 128, 256.

- The equatorial encoding is the **phase encoding known from the literature**
  (e.g., IBM Quantum Learning documents `P(phi)|+>`). It is adopted here as a
  known experimental reference, **not** as a Hubstry invention.
- [DERIVED + OBSERVED] Equatorial fidelity depends only on the phase
  difference: `F = cos^2(dtheta/2)`, hence uniform adjacent fidelity
  `F_n = cos^2(pi/n)` at every n. Verified symbolically and numerically
  for all state pairs.
- [OBSERVED] The baseline encoding shows adjacent fidelity dependent on the
  absolute position k for n >= 8 (e.g., n=8: F ranges 0.75 to 0.8536).
  Position dependence also proven symbolically.

**64-profile lattice** (`lattice64.py`):

- 64 harmonic profiles encoded as the 2^6 = 64 computational-basis states
  of a 6-qubit register; consistency projector P_C over the 7 consistent
  profiles of Paper 2 (DOI 10.5281/zenodo.18776462).
- This is a **computational encoding**: it does NOT demonstrate six physical
  qubits, quantum advantage, or quantum security.

### Validation

- 136 pytest cases passing (collected cases, not test functions).
- Required Change #1: implementation-to-baseline fidelity verified over
  520 (k,n) combinations against `harmonic_state.harmonic_qubit`, zero drift.
- Reproduced in 3 independent environments (WSL, two sandboxes).

### Explicitly NOT claimed

- No quantum security, no quantum advantage, no cryptographic security level.
- Fidelity and anomaly scores are experimental similarity measurements.
- `post-quantum/rho3_bound.py` remains experimental and **not audited**;
  a mathematical inconsistency in its claimed bound is under separate review
  (`research/audit-rho3-bound`). Do not cite its results until the audit
  concludes.

Full experimental record: `docs/research/pr1-quantum-encoding.md`.
