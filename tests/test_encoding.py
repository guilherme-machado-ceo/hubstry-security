"""
tests/test_encoding.py — PR1-C tests for quantum/encoding_compare.py.

Covers: normalization, periodicity, fidelity, equatorial encoding closed
form, uniformity, and the observed non-uniformity of the current encoding.

Run from repository root:  pytest tests/ -v
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from quantum.encoding_compare import (
    SUBDIVISIONS,
    current_encoding,
    equatorial_encoding,
    measure_encoding,
    phase_sensitivity,
    state_fidelity,
)

TOL = 1e-12
ALL_N = SUBDIVISIONS  # (4, 8, 12, 16, 32, 64, 128, 256)


# --- Normalization -----------------------------------------------------------

@pytest.mark.parametrize("n", ALL_N)
@pytest.mark.parametrize("fn", [current_encoding, equatorial_encoding])
def test_states_are_normalized(fn, n):
    for k in range(n):
        theta = 2.0 * math.pi * k / n
        assert abs(np.linalg.norm(fn(theta)) - 1.0) < TOL


# --- Periodicity -------------------------------------------------------------

@pytest.mark.parametrize("fn", [current_encoding, equatorial_encoding])
def test_periodicity_theta_0_equals_2pi(fn):
    # Physical periodicity: F(psi(0), psi(2*pi)) == 1
    assert abs(state_fidelity(fn(0.0), fn(2.0 * math.pi)) - 1.0) < TOL


# --- Equatorial encoding: closed form and uniformity -------------------------

@pytest.mark.parametrize("n", ALL_N)
def test_equatorial_matches_closed_form_all_pairs(n):
    # DERIVED, verified numerically: F = cos^2(dtheta/2) for every pair.
    report = measure_encoding("equatorial", equatorial_encoding, n)
    assert report.matches_closed_form


@pytest.mark.parametrize("n", ALL_N)
def test_equatorial_adjacent_fidelity_is_uniform(n):
    report = measure_encoding("equatorial", equatorial_encoding, n)
    assert report.uniformity_gap < TOL
    assert abs(report.fidelity_mean - math.cos(math.pi / n) ** 2) < TOL


def test_equatorial_sensitivity_is_position_independent():
    _, gap = phase_sensitivity(equatorial_encoding, 32, perturbation=0.05)
    assert gap < TOL


# --- Current encoding: reproduces the observed k-dependence ------------------

def test_current_encoding_non_uniform_for_n8():
    # OBSERVED: adjacent fidelity varies with position k for n >= 8.
    report = measure_encoding("current", current_encoding, 8)
    assert report.uniformity_gap > 1e-3
    assert abs(report.fidelity_min - 0.75) < 1e-9        # reproduces reported 0.75
    assert abs(report.fidelity_max - 0.853553) < 1e-6    # reproduces reported 0.853553


def test_current_encoding_uniform_at_n4():
    # OBSERVED: at n=4 the two encodings coincide (F = 0.5 everywhere).
    report = measure_encoding("current", current_encoding, 4)
    assert report.uniformity_gap < TOL
    assert abs(report.fidelity_mean - 0.5) < TOL


def test_current_encoding_sensitivity_depends_on_position():
    _, gap = phase_sensitivity(current_encoding, 32, perturbation=0.05)
    assert gap > 1e-6


# --- Fidelity sanity ---------------------------------------------------------

def test_fidelity_bounds_and_identity():
    a = equatorial_encoding(0.3)
    assert abs(state_fidelity(a, a) - 1.0) < TOL
    b = equatorial_encoding(0.3 + math.pi)  # antipodal on the equator
    assert abs(state_fidelity(a, b)) < 1e-9  # orthogonal
