"""
tests/test_capacity.py — addressing capacity of harmonic phase encodings.

Checks the numerical quantities in quantum/capacity.py against known closed
forms (equatorial qubit: 2/n and 1 bit; qudit: 1 and log2 n), the closed
form of the reference encoding's adjacent fidelity, consistency with the
baseline quantum/harmonic_state.py, and basic bounds.

Run from repository root:  pytest tests/ -v
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from quantum import capacity as cap  # noqa: E402
from quantum.harmonic_state import fidelity, harmonic_family  # noqa: E402

NS = (2, 3, 4, 5, 8, 12, 16, 32, 64, 128, 256)


@pytest.mark.parametrize("encoding", sorted(cap.ENCODINGS))
@pytest.mark.parametrize("n", (1, 2, 7, 12, 64))
def test_states_are_normalized(encoding, n):
    states = cap.ENCODINGS[encoding](n)
    assert states.shape[0] == n
    assert np.allclose(np.linalg.norm(states, axis=1), 1.0)


@pytest.mark.parametrize("bad", (0, -3, 2.5, True))
def test_invalid_n_is_rejected(bad):
    with pytest.raises(ValueError):
        cap.equatorial_states(bad)


# --- equatorial qubit: DERIVED closed forms -----------------------------------


@pytest.mark.parametrize("n", NS)
def test_equatorial_success_is_two_over_n(n):
    assert cap.srm_success_probability(cap.equatorial_states(n)) == pytest.approx(
        cap.equatorial_success_closed_form(n), abs=1e-10
    )


@pytest.mark.parametrize("n", NS)
def test_equatorial_holevo_is_one_bit(n):
    assert cap.holevo_chi(cap.equatorial_states(n)) == pytest.approx(1.0, abs=1e-10)


@pytest.mark.parametrize("n", NS)
def test_equatorial_adjacent_fidelity_is_uniform(n):
    adj = cap.adjacent_fidelities(cap.equatorial_states(n))
    assert np.allclose(adj, math.cos(math.pi / n) ** 2, atol=1e-12)


# --- qudit: DERIVED closed forms ------------------------------------------------


@pytest.mark.parametrize("n", (2, 3, 8, 12, 64))
def test_qudit_states_are_orthonormal(n):
    s = cap.qudit_states(n)
    assert np.allclose(s.conj() @ s.T, np.eye(n), atol=1e-10)


@pytest.mark.parametrize("n", (2, 3, 8, 12, 64))
def test_qudit_success_is_one_and_holevo_is_log2_n(n):
    s = cap.qudit_states(n)
    assert cap.srm_success_probability(s) == pytest.approx(1.0, abs=1e-10)
    assert cap.holevo_chi(s) == pytest.approx(math.log2(n), abs=1e-10)


# --- reference encoding ------------------------------------------------------------


@pytest.mark.parametrize("n", (4, 8, 12, 16, 32, 64, 128, 256))
def test_reference_adjacent_fidelity_matches_closed_form(n):
    adj = cap.adjacent_fidelities(cap.reference_states(n))
    expected = [cap.reference_adjacent_fidelity_closed_form(k, n) for k in range(n)]
    assert np.allclose(adj, expected, atol=1e-12)


@pytest.mark.parametrize("n", (4, 8, 12, 64))
def test_reference_matches_baseline_module(n):
    family = harmonic_family(n)
    baseline = [fidelity(family[k], family[(k + 1) % n]) for k in range(n)]
    assert np.allclose(cap.adjacent_fidelities(cap.reference_states(n)), baseline, atol=1e-12)


@pytest.mark.parametrize("n", (8, 12, 64))
def test_reference_adjacent_fidelity_depends_on_position(n):
    adj = cap.adjacent_fidelities(cap.reference_states(n))
    assert adj.max() - adj.min() > 1e-6


@pytest.mark.parametrize("n", (1, 2, 3, 4, 8, 12, 64, 256))
def test_reference_holevo_matches_closed_form(n):
    assert cap.holevo_chi(cap.reference_states(n)) == pytest.approx(
        cap.reference_chi_closed_form(n), abs=1e-10
    )


@pytest.mark.parametrize("n", (3, 8, 64))
def test_reference_does_not_reach_one_bit(n):
    assert cap.holevo_chi(cap.reference_states(n)) < cap.holevo_chi(cap.equatorial_states(n)) - 0.1


def test_reference_n8_range_matches_pr1_record():
    adj = cap.adjacent_fidelities(cap.reference_states(8))
    assert adj.min() == pytest.approx(0.75, abs=1e-4)
    assert adj.max() == pytest.approx((2 + math.sqrt(2)) / 4, abs=1e-4)


# --- general bounds -----------------------------------------------------------------


@pytest.mark.parametrize("encoding", sorted(cap.ENCODINGS))
@pytest.mark.parametrize("n", (2, 3, 8, 12, 64))
def test_bounds(encoding, n):
    s = cap.ENCODINGS[encoding](n)
    p = cap.srm_success_probability(s)
    chi = cap.holevo_chi(s)
    dim = s.shape[1]
    assert 1.0 / n - 1e-12 <= p <= 1.0 + 1e-12
    assert p <= dim / n + 1e-10  # at most dim states are perfectly distinguishable
    assert -1e-12 <= chi <= min(math.log2(n), math.log2(dim)) + 1e-10


def test_capacity_table_rows_and_flags():
    rows = cap.capacity_table((8, 12))
    assert len(rows) == 6
    assert {r["encoding"] for r in rows} == {"reference", "equatorial", "qudit"}
    for r in rows:
        assert r["srm_is_optimal"] == (r["encoding"] != "reference")
