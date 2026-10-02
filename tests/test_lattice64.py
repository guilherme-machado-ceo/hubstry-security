"""
tests/test_lattice64.py — PR1-C tests for quantum/lattice64.py.

Covers: 64-profile computational-basis encoding, consistency projector
properties, and consistency/anomaly behavior. All values are experimental
consistency measurements, not cryptographic security levels.

Run from repository root:  pytest tests/ -v
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from quantum.lattice64 import (
    CONSISTENT_PROFILES,
    DIM,
    N_QUBITS,
    anomaly_score,
    consistency_probability,
    consistency_projector,
    encode_profile,
    noisy_profile,
    superposition_state,
)

TOL = 1e-12


# --- Encoding ----------------------------------------------------------------

def test_dimension_matches_encoding():
    assert N_QUBITS == 6
    assert DIM == 64  # 2^6: computational encoding of 64 profiles


def test_consistent_set_matches_paper2():
    assert CONSISTENT_PROFILES == frozenset({0, 1, 2, 4, 8, 16, 32})
    assert len(CONSISTENT_PROFILES) == 7


@pytest.mark.parametrize("p", range(64))
def test_encode_profile_is_unit_basis_vector(p):
    s = encode_profile(p)
    assert abs(np.linalg.norm(s) - 1.0) < TOL
    assert s[p] == 1.0
    assert np.count_nonzero(s) == 1


def test_encode_profile_rejects_out_of_range():
    with pytest.raises(ValueError):
        encode_profile(64)
    with pytest.raises(ValueError):
        encode_profile(-1)


# --- Consistency projector ---------------------------------------------------

def test_projector_is_idempotent():
    P = consistency_projector()
    assert np.allclose(P @ P, P, atol=TOL)


def test_projector_is_hermitian():
    P = consistency_projector()
    assert np.allclose(P, P.conj().T, atol=TOL)


def test_projector_trace_equals_seven():
    P = consistency_projector()
    assert abs(np.trace(P) - 7.0) < TOL  # 7 consistent profiles


# --- Consistency probability -------------------------------------------------

@pytest.mark.parametrize("p", sorted(CONSISTENT_PROFILES))
def test_consistent_profiles_measure_one(p):
    assert abs(consistency_probability(encode_profile(p)) - 1.0) < TOL


@pytest.mark.parametrize("p", [3, 5, 6, 7, 9, 21, 42, 63])
def test_inconsistent_profiles_measure_zero(p):
    assert p not in CONSISTENT_PROFILES
    assert abs(consistency_probability(encode_profile(p))) < TOL


def test_superposition_gives_intermediate_probability():
    # One consistent + one inconsistent -> P = 0.5 (uniform superposition).
    s = superposition_state([0, 3])
    assert abs(consistency_probability(s) - 0.5) < TOL
    assert abs(anomaly_score(s) - 0.5) < TOL


def test_superposition_of_all_consistent_measures_one():
    s = superposition_state(sorted(CONSISTENT_PROFILES))
    assert abs(consistency_probability(s) - 1.0) < TOL


def test_noise_produces_intermediate_anomaly():
    s = noisy_profile(0, noise=0.05, seed=42)
    p = consistency_probability(s)
    assert 0.0 < p < 1.0


def test_anomaly_score_is_complement():
    s = noisy_profile(0, noise=0.10, seed=7)
    assert abs(anomaly_score(s) + consistency_probability(s) - 1.0) < TOL
