"""
quantum/lattice64.py — 64 harmonic profiles encoded in a 6-qubit register
==========================================================================

PR1-B (feat/pqc-real-quantum-lattice). NumPy-only. No CUDA-Q, no QPU.

DOCUMENTATION RULE (keep in READMEs, papers and talks):

    2^6 = 64 is a COMPUTATIONAL ENCODING of 64 classical profiles into the
    computational basis of a 6-qubit register. It is NOT evidence that the
    system possesses or uses six physical qubits, and it is NOT a claim of
    quantum advantage or quantum security.

    Three layers must stay distinct:
      - mathematical encoding          (this module)
      - quantum-state representation   (simulated statevector)
      - physical quantum computation   (NOT claimed, NOT tested here)

Ref: Paper 2 (CC BY 4.0): DOI 10.5281/zenodo.18776462 — 64 profiles,
7 consistent under the paper's consistency criterion.

The consistency projector

    P_C = sum_{sigma in Sigma_C} |sigma><sigma|,
    Sigma_C = {0, 1, 2, 4, 8, 16, 32}

is treated here as an experimental observable over the encoded space.
Consistency probabilities are similarity/consistency measurements; they are
NOT cryptographic security levels.

Run:
    python -m quantum.lattice64    (from repository root)

Author: Hubstry Deep Tech (guilhermemachado.ceo@hubstry.dev)
License: CC BY-NC-SA 4.0
"""

from __future__ import annotations

import numpy as np

N_QUBITS = 6
DIM = 2 ** N_QUBITS  # 64 computational-basis states (encoding, not physics)

# 7 consistent profiles from Paper 2: empty profile + single-bit profiles.
CONSISTENT_PROFILES = frozenset({0, 1, 2, 4, 8, 16, 32})


def encode_profile(profile: int) -> np.ndarray:
    """
    Encode a profile (0..63) as the computational-basis vector |profile>.

    This is an ENCODING: a deterministic statevector with amplitude 1 at
    position `profile`. No physical interpretation is claimed.
    """
    if not 0 <= profile < DIM:
        raise ValueError(f"profile out of [0, 63]: {profile}")
    state = np.zeros(DIM, dtype=np.complex128)
    state[profile] = 1.0
    return state


def consistency_projector() -> np.ndarray:
    """P_C = sum over Sigma_C of |sigma><sigma| (diagonal 64x64 projector)."""
    P = np.zeros((DIM, DIM), dtype=np.complex128)
    for s in CONSISTENT_PROFILES:
        P[s, s] = 1.0
    return P


def consistency_probability(state: np.ndarray) -> float:
    """
    P(consistent) = <psi| P_C |psi>, in [0, 1].

    Properties (numerically verified in tests/, not assumed):
      - encoded consistent basis profile   -> 1.0
      - encoded inconsistent basis profile -> 0.0
      - superpositions / noisy states      -> intermediate values, which is
        where the experimentally relevant signal lives.
    """
    state = np.asarray(state, dtype=np.complex128)
    P = consistency_projector()
    return float(np.real(state.conj() @ P @ state))


def anomaly_score(state: np.ndarray) -> float:
    """Experimental consistency-anomaly indicator: 1 - P(consistent)."""
    return 1.0 - consistency_probability(state)


def superposition_state(profiles: list[int]) -> np.ndarray:
    """Uniform superposition (1/sqrt(k)) * sum |p_i> over the given profiles."""
    if not profiles:
        raise ValueError("profiles must be non-empty")
    state = np.zeros(DIM, dtype=np.complex128)
    for p in profiles:
        state[p] = 1.0
    return state / np.linalg.norm(state)


def noisy_profile(profile: int, noise: float, seed: int = 42) -> np.ndarray:
    """Encoded |profile> plus complex Gaussian perturbation, renormalized."""
    rng = np.random.default_rng(seed)
    state = encode_profile(profile) + noise * (
        rng.standard_normal(DIM) + 1j * rng.standard_normal(DIM)
    )
    return state / np.linalg.norm(state)


def demo() -> None:
    print("=" * 66)
    print("  lattice64 — 64 profiles encoded in 6-qubit computational basis")
    print("  encoding != physical qubits | Ref: DOI 10.5281/zenodo.18776462")
    print("=" * 66)

    print(f"\n  {'Profile':>7}  {'Bits':>7}  {'P(consist.)':>12}  {'Anomaly':>8}  Class")
    for p in [0, 1, 2, 4, 8, 16, 32, 3, 5, 7, 21, 42, 63]:
        s = encode_profile(p)
        pc = consistency_probability(s)
        cls = "consistent" if p in CONSISTENT_PROFILES else "inconsistent"
        print(f"  {p:>7}  {format(p, '06b'):>7}  {pc:>12.4f}  {anomaly_score(s):>8.4f}  {cls}")

    print("\n  -- Superpositions (experimental regime) --")
    for combo in ([0, 3], [1, 2, 63], [0, 1, 2, 4, 8, 16, 32]):
        s = superposition_state(combo)
        print(f"  {str(combo):>28}: P={consistency_probability(s):.4f}  "
              f"anomaly={anomaly_score(s):.4f}")

    print("\n  -- Noise: consistent profile + 5% perturbation --")
    s = noisy_profile(0, noise=0.05)
    print(f"  |000000> + noise: P={consistency_probability(s):.4f}  "
          f"anomaly={anomaly_score(s):.4f}")

    print("\n  Classification: values above = OBSERVED (numerical).")
    print("  NOT TESTED: security, anomaly-detection advantage, quantum advantage.")
    print("=" * 66)


if __name__ == "__main__":
    demo()
