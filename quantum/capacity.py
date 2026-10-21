"""
quantum/capacity.py — Addressing capacity of harmonic phase encodings
=====================================================================

NumPy-only. No CUDA-Q, no QPU, no cloud.

Research question:
    How many harmonic addresses can be recovered from a quantum encoding of
    n phases theta_k = 2*pi*k/n, and how does the answer change between a
    single qubit and an n-level system (qudit)?

Encodings compared (n addresses, equiprobable):

  REFERENCE   (quantum/harmonic_state.py, single qubit):
      |psi(theta)> = cos(theta/2)|0> + exp(i*theta) sin(theta/2)|1>
  EQUATORIAL  (single qubit, Bloch-sphere equator):
      |psi_e(theta)> = (|0> + exp(i*theta)|1>) / sqrt(2)
  QUDIT       (n levels, discrete-Fourier states):
      |f_k> = (1/sqrt(n)) * sum_j exp(2*pi*i*j*k/n) |j>

Quantities:
  - adjacent fidelity |<psi_k|psi_{k+1}>|^2;
  - success probability of the square-root measurement (SRM). For
    symmetric (geometrically uniform) state sets, such as EQUATORIAL and
    QUDIT, the SRM is the optimal minimum-error measurement (Ban et al.
    1997; Eldar & Forney 2001). For REFERENCE, which is not symmetric, the
    SRM value is only a lower bound on the optimum;
  - Holevo quantity chi = S(rho_avg) for pure states, in bits: an upper
    bound on the information accessible per measurement (Holevo 1973).

Known closed forms, verified numerically in tests/test_capacity.py:
  EQUATORIAL: P_srm = 2/n (n >= 2),  chi = 1 bit (n >= 2)
  QUDIT:      P_srm = 1,             chi = log2(n) bits
  REFERENCE:  F_adj(k, n) = cos^4(pi/n) + sin^2(pi/n) cos^2((2k+1) pi/n)
              chi = 2 - (3/4) log2(3) ~ 0.8113 bits for every n >= 3: the
              average state has eigenvalues 3/4 and 1/4, so the reference
              encoding does not reach the 1-bit limit of a qubit.

Classification (project governance):
  DERIVED  = known closed form, verified numerically here.
  OBSERVED = computed numerically here without a closed form.
  No security, quantum-advantage or hardware claim is made.

Run:
    python -m quantum.capacity        (from repository root)

Author: Hubstry Deep Tech (guilhermemachado.ceo@hubstry.dev)
License: CC BY-NC-SA 4.0
"""

from __future__ import annotations

import math
from typing import Callable

import numpy as np

SUBDIVISIONS: tuple[int, ...] = (2, 3, 4, 8, 12, 16, 32, 64, 128, 256)
_EIG_TOL = 1e-12


# ---------------------------------------------------------------------------
# Encodings: each returns an (n, d) array whose rows are normalized states.
# ---------------------------------------------------------------------------


def _check_n(n: int) -> None:
    if not isinstance(n, int) or isinstance(n, bool) or n < 1:
        raise ValueError("n must be a positive integer")


def reference_states(n: int) -> np.ndarray:
    """Reference single-qubit encoding (same formula as harmonic_state.py)."""
    _check_n(n)
    theta = 2.0 * np.pi * np.arange(n) / n
    return np.stack([np.cos(theta / 2.0), np.exp(1j * theta) * np.sin(theta / 2.0)], axis=1)


def equatorial_states(n: int) -> np.ndarray:
    """Equatorial single-qubit encoding."""
    _check_n(n)
    theta = 2.0 * np.pi * np.arange(n) / n
    return np.stack([np.ones(n), np.exp(1j * theta)], axis=1) / math.sqrt(2.0)


def qudit_states(n: int) -> np.ndarray:
    """Discrete-Fourier states of an n-level system."""
    _check_n(n)
    j = np.arange(n)
    return np.exp(2j * np.pi * np.outer(j, j) / n) / math.sqrt(n)


ENCODINGS: dict[str, Callable[[int], np.ndarray]] = {
    "reference": reference_states,
    "equatorial": equatorial_states,
    "qudit": qudit_states,
}


# ---------------------------------------------------------------------------
# Quantities
# ---------------------------------------------------------------------------


def adjacent_fidelities(states: np.ndarray) -> np.ndarray:
    """|<psi_k|psi_{k+1 mod n}>|^2 for every k."""
    nxt = np.roll(states, -1, axis=0)
    return np.abs(np.sum(states.conj() * nxt, axis=1)) ** 2


def _psd_power(matrix: np.ndarray, power: float) -> np.ndarray:
    """Power of a Hermitian PSD matrix on its support (pseudo-inverse for <0)."""
    w, v = np.linalg.eigh((matrix + matrix.conj().T) / 2.0)
    wp = np.zeros_like(w)
    mask = w > _EIG_TOL
    wp[mask] = w[mask] ** power
    return (v * wp) @ v.conj().T


def srm_success_probability(states: np.ndarray) -> float:
    """Average success probability of the square-root measurement.

    Equiprobable states |psi_k>; POVM elements M_k = R |psi_k><psi_k| R with
    R = (sum_k |psi_k><psi_k|)^(-1/2) on its support.
    """
    gram_sum = states.T @ states.conj()  # sum_k |psi_k><psi_k|
    r = _psd_power(gram_sum, -0.5)
    amplitudes = np.einsum("ij,kj->ki", r, states)  # R|psi_k>
    overlaps = np.sum(states.conj() * amplitudes, axis=1)
    return float(np.mean(np.abs(overlaps) ** 2))


def holevo_chi(states: np.ndarray) -> float:
    """Holevo quantity S(rho_avg) in bits for equiprobable pure states."""
    rho = states.T @ states.conj() / states.shape[0]
    w = np.linalg.eigvalsh((rho + rho.conj().T) / 2.0)
    w = w[w > _EIG_TOL]
    return float(-np.sum(w * np.log2(w)))


# ---------------------------------------------------------------------------
# Closed forms (DERIVED)
# ---------------------------------------------------------------------------


def reference_adjacent_fidelity_closed_form(k: int, n: int) -> float:
    """cos^4(pi/n) + sin^2(pi/n) cos^2((2k+1) pi/n)."""
    _check_n(n)
    a = math.pi / n
    return math.cos(a) ** 4 + math.sin(a) ** 2 * math.cos((2 * k + 1) * math.pi / n) ** 2


def reference_chi_closed_form(n: int) -> float:
    """Holevo quantity of the reference encoding.

    For n >= 3 the average state is [[1/2, -i/4], [i/4, 1/2]], with
    eigenvalues 3/4 and 1/4, so chi = 2 - (3/4) log2 3. For n = 2 the two
    states are orthogonal (1 bit); for n = 1, 0 bits.
    """
    _check_n(n)
    if n == 1:
        return 0.0
    if n == 2:
        return 1.0
    return 2.0 - 0.75 * math.log2(3.0)


def equatorial_success_closed_form(n: int) -> float:
    """Optimal success probability for n equatorial qubit states: 2/n (n >= 2)."""
    _check_n(n)
    return 1.0 if n == 1 else 2.0 / n


def equatorial_chi_closed_form(n: int) -> float:
    """Holevo quantity for n equatorial qubit states: 1 bit (n >= 2)."""
    _check_n(n)
    return 0.0 if n == 1 else 1.0


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------


def capacity_table(subdivisions: tuple[int, ...] = SUBDIVISIONS) -> list[dict]:
    rows = []
    for n in subdivisions:
        for name, encode in ENCODINGS.items():
            states = encode(n)
            adj = adjacent_fidelities(states)
            rows.append(
                {
                    "n": n,
                    "encoding": name,
                    "dimension": states.shape[1],
                    "adjacent_fidelity_min": float(adj.min()),
                    "adjacent_fidelity_max": float(adj.max()),
                    "srm_success": srm_success_probability(states),
                    "holevo_chi_bits": holevo_chi(states),
                    "srm_is_optimal": name in ("equatorial", "qudit"),
                }
            )
    return rows


def main() -> None:
    print("HALE-Q addressing capacity — NumPy simulation (no QPU)")
    print(f"{'n':>4} {'encoding':<11} {'dim':>4} {'F_adj min':>10} {'F_adj max':>10} "
          f"{'P_success':>10} {'chi (bits)':>10}")
    for r in capacity_table():
        flag = "" if r["srm_is_optimal"] else "  (SRM lower bound)"
        print(f"{r['n']:>4} {r['encoding']:<11} {r['dimension']:>4} "
              f"{r['adjacent_fidelity_min']:>10.4f} {r['adjacent_fidelity_max']:>10.4f} "
              f"{r['srm_success']:>10.4f} {r['holevo_chi_bits']:>10.4f}{flag}")


if __name__ == "__main__":
    main()
