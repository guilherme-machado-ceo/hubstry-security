"""
quantum/encoding_compare.py — Harmonic phase encodings: current vs equatorial
==============================================================================

PR1-A (feat/pqc-real-quantum-lattice). NumPy-only. No CUDA-Q, no QPU, no cloud.

Compares two single-qubit encodings of a harmonic phase theta_k = 2*pi*k/n:

  A) CURRENT (repo baseline, quantum/harmonic_state.py):
        |psi(theta)> = cos(theta/2)|0> + exp(i*theta) sin(theta/2)|1>

  B) EQUATORIAL (Bloch-sphere equator):
        |psi_e(theta)> = (|0> + exp(i*theta)|1>) / sqrt(2)

Research question (approved scope):
    Does the equatorial encoding eliminate the dependence of adjacent-state
    fidelity on the position k observed in the current encoding?

Result classification follows project governance:
    OBSERVED  = measured numerically in this module
    DERIVED   = closed-form expression, additionally verified numerically
    No security advantage is claimed for either encoding.

Run:
    python -m quantum.encoding_compare        (from repository root)

Author: Hubstry Deep Tech (guilhermemachado.ceo@hubstry.dev)
License: CC BY-NC-SA 4.0
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Callable

import numpy as np

SUBDIVISIONS: tuple[int, ...] = (4, 8, 12, 16, 32, 64, 128, 256)

EncodingFn = Callable[[float], np.ndarray]


# --- Encodings ---------------------------------------------------------------

def current_encoding(theta: float) -> np.ndarray:
    """Baseline encoding: cos(theta/2)|0> + exp(i*theta) sin(theta/2)|1>."""
    return np.array(
        [math.cos(theta / 2.0), np.exp(1j * theta) * math.sin(theta / 2.0)],
        dtype=np.complex128,
    )


def equatorial_encoding(theta: float) -> np.ndarray:
    """Equatorial encoding: (|0> + exp(i*theta)|1>) / sqrt(2)."""
    return np.array(
        [1.0 / math.sqrt(2.0), np.exp(1j * theta) / math.sqrt(2.0)],
        dtype=np.complex128,
    )


# --- Metrics -----------------------------------------------------------------

def state_fidelity(a: np.ndarray, b: np.ndarray) -> float:
    """Pure-state fidelity |<a|b>|^2."""
    return float(abs(np.vdot(a, b)) ** 2)


@dataclass
class EncodingReport:
    encoding: str
    subdivision: int
    delta_theta: float
    fidelity_min: float
    fidelity_max: float
    fidelity_mean: float
    fidelity_std: float
    uniformity_gap: float          # max - min; 0.0 = translation-invariant
    max_norm_error: float          # | ||psi|| - 1 | over all states
    periodicity_fidelity: float    # F(psi(0), psi(2*pi)); 1.0 = periodic
    matches_closed_form: bool      # equatorial: F == cos^2(delta/2) for ALL pairs


def measure_encoding(name: str, fn: EncodingFn, n: int) -> EncodingReport:
    """Measure adjacent-fidelity statistics over the full subdivision grid."""
    thetas = [2.0 * math.pi * k / n for k in range(n)]
    states = [fn(t) for t in thetas]

    norms = [float(np.linalg.norm(s)) for s in states]
    max_norm_error = max(abs(x - 1.0) for x in norms)

    adj = [
        state_fidelity(states[k], states[(k + 1) % n])
        for k in range(n)
    ]
    adj_arr = np.asarray(adj)

    periodicity = state_fidelity(fn(0.0), fn(2.0 * math.pi))

    # Closed-form check: equatorial must satisfy F = cos^2(dtheta/2) for
    # EVERY pair (k, j), not only adjacent ones.
    closed_ok = True
    for k in range(n):
        for j in range(n):
            dtheta = thetas[k] - thetas[j]
            expected = math.cos(dtheta / 2.0) ** 2
            if abs(state_fidelity(states[k], states[j]) - expected) > 1e-12:
                closed_ok = False
                break
        if not closed_ok:
            break

    return EncodingReport(
        encoding=name,
        subdivision=n,
        delta_theta=2.0 * math.pi / n,
        fidelity_min=float(adj_arr.min()),
        fidelity_max=float(adj_arr.max()),
        fidelity_mean=float(adj_arr.mean()),
        fidelity_std=float(adj_arr.std()),
        uniformity_gap=float(adj_arr.max() - adj_arr.min()),
        max_norm_error=max_norm_error,
        periodicity_fidelity=periodicity,
        matches_closed_form=closed_ok,
    )


def phase_sensitivity(fn: EncodingFn, n: int, perturbation: float = 0.05) -> tuple[float, float]:
    """
    Fidelity drop under a fixed phase perturbation, as (mean, max-min) over k.

    A translation-invariant encoding responds identically at every position;
    this is the property that matters for anomaly detection (E-C).
    """
    drops = []
    for k in range(n):
        theta = 2.0 * math.pi * k / n
        drops.append(1.0 - state_fidelity(fn(theta), fn(theta + perturbation)))
    arr = np.asarray(drops)
    return float(arr.mean()), float(arr.max() - arr.min())


# --- Report ------------------------------------------------------------------

def run_comparison(subdivisions: tuple[int, ...] = SUBDIVISIONS) -> list[EncodingReport]:
    reports: list[EncodingReport] = []
    for n in subdivisions:
        reports.append(measure_encoding("current", current_encoding, n))
        reports.append(measure_encoding("equatorial", equatorial_encoding, n))
    return reports


def print_report(reports: list[EncodingReport]) -> None:
    print("=" * 78)
    print("  E-A+ Encoding Comparison: current vs equatorial (PR1-A)")
    print("  Classification: numeric values = OBSERVED | F=cos^2(d/2) = DERIVED")
    print("  No security advantage is claimed for either encoding.")
    print("=" * 78)

    header = (f"  {'enc':>10} {'n':>4} {'dTheta':>8} {'F_min':>8} {'F_max':>8} "
              f"{'F_mean':>8} {'F_std':>9} {'unif.gap':>9} {'period':>7}")
    print("\n" + header)
    print("  " + "-" * (len(header) - 2))
    for r in reports:
        print(
            f"  {r.encoding:>10} {r.subdivision:>4} {r.delta_theta:>8.4f} "
            f"{r.fidelity_min:>8.4f} {r.fidelity_max:>8.4f} {r.fidelity_mean:>8.4f} "
            f"{r.fidelity_std:>9.2e} {r.uniformity_gap:>9.2e} "
            f"{r.periodicity_fidelity:>7.4f}"
        )

    print("\n  Normalization: max | ||psi|| - 1 | over all states")
    for r in reports:
        print(f"    {r.encoding:>10} n={r.subdivision:>4}: {r.max_norm_error:.2e}")

    print("\n  Closed form F = cos^2(dTheta/2), verified for ALL pairs (k, j):")
    for r in reports:
        verdict = "HOLDS" if r.matches_closed_form else "DOES NOT HOLD"
        print(f"    {r.encoding:>10} n={r.subdivision:>4}: {verdict}")

    print("\n  Phase sensitivity to perturbation delta=0.05 rad: mean drop / gap over k")
    for n in SUBDIVISIONS:
        mc, gc = phase_sensitivity(current_encoding, n)
        me, ge = phase_sensitivity(equatorial_encoding, n)
        print(f"    n={n:>4}: current mean={mc:.6f} gap={gc:.2e} | "
              f"equatorial mean={me:.6f} gap={ge:.2e}")

    print("\n  Summary:")
    print("    [OBSERVED] current encoding: adjacent fidelity depends on k")
    print("               (uniformity gap > 0 for n >= 8).")
    print("    [OBSERVED] equatorial encoding: uniformity gap ~ 0 at every n;")
    print("               sensitivity to a fixed perturbation is position-independent.")
    print("    [DERIVED]  equatorial: F(dTheta) = cos^2(dTheta/2), hence uniform grid")
    print("               F_n = cos^2(pi/n); verified numerically for all pairs.")
    print("    [NOT TESTED] any security, anomaly-detection or quantum-advantage claim.")
    print("=" * 78)


def main() -> None:
    print_report(run_comparison())


if __name__ == "__main__":
    main()
