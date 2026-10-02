"""Quantum-inspired harmonic-state experiments for Hubstry Security."""
from __future__ import annotations
from dataclasses import dataclass
import cmath
import math
from typing import Iterable
import numpy as np

@dataclass(frozen=True)
class HarmonicState:
    subdivision: int
    index: int
    theta: float
    amplitudes: tuple[complex, complex]

def harmonic_phase(index: int, subdivision: int) -> float:
    """Return 2*pi*k/n for the kth harmonic subdivision."""
    if subdivision <= 0:
        raise ValueError("subdivision must be positive")
    if not 0 <= index < subdivision:
        raise ValueError("index must satisfy 0 <= index < subdivision")
    return 2.0 * math.pi * index / subdivision

def harmonic_qubit(index: int, subdivision: int) -> HarmonicState:
    """Encode one harmonic phase as a normalized single-qubit state."""
    theta = harmonic_phase(index, subdivision)
    a0 = math.cos(theta / 2.0)
    a1 = cmath.exp(1j * theta) * math.sin(theta / 2.0)
    return HarmonicState(subdivision, index, theta, (complex(a0), complex(a1)))

def fidelity(a: HarmonicState, b: HarmonicState) -> float:
    """Pure-state fidelity |<a|b>|^2."""
    va = np.asarray(a.amplitudes, dtype=np.complex128)
    vb = np.asarray(b.amplitudes, dtype=np.complex128)
    return float(abs(np.vdot(va, vb)) ** 2)

def phase_distance(a: HarmonicState, b: HarmonicState) -> float:
    """Shortest circular phase distance in radians."""
    delta = (a.theta - b.theta + math.pi) % (2.0 * math.pi) - math.pi
    return abs(delta)

def harmonic_family(subdivision: int) -> list[HarmonicState]:
    return [harmonic_qubit(k, subdivision) for k in range(subdivision)]

def adjacent_fidelities(subdivisions: Iterable[int]) -> list[dict]:
    rows = []
    for n in subdivisions:
        states = harmonic_family(n)
        for k, state in enumerate(states):
            nxt = states[(k + 1) % n]
            rows.append({
                "subdivision": n,
                "index": k,
                "next_index": nxt.index,
                "phase_distance_rad": phase_distance(state, nxt),
                "fidelity": fidelity(state, nxt),
            })
    return rows

def six_qubit_profile_state(profile: int) -> np.ndarray:
    """Return a computational-basis vector for one of 64 profiles."""
    if not 0 <= profile < 64:
        raise ValueError("profile must be in [0, 63]")
    state = np.zeros(64, dtype=np.complex128)
    state[profile] = 1.0
    return state

if __name__ == "__main__":
    for row in adjacent_fidelities([4, 8, 12, 16, 32, 64])[:12]:
        print(row)
