"""
tests/test_quantizer_composition.py — exact verification of quantizer composition.

Exhaustive checks over finite ranges, with rational arithmetic, of the two
classification theorems, the divergence formulas in both domains (interval
and circle), the m = 1 edge case, the worked examples and counterexamples of
the source working paper, and path dependence. A finite sweep is regression
evidence; it does not replace the general proofs.

Run from repository root:  pytest tests/ -v
"""

from __future__ import annotations

import sys
from fractions import Fraction as F
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from quantum import quantizer_composition as qc  # noqa: E402

M_MAX, N_MAX = 24, 60


def _pairs(m_lo=1, m_hi=M_MAX, n_hi=N_MAX):
    return [(m, n) for m in range(m_lo, m_hi + 1) for n in range(1, n_hi + 1)]


# --- Theorem 1 (floor) ----------------------------------------------------------------


def test_theorem1_floor_classification_exhaustive():
    for m, n in _pairs():
        assert (qc.divergence(qc.floor_q, m, n) == 0) == qc.floor_equivalent(m, n), (m, n)


# --- Theorem 2 (round), both domains ------------------------------------------------------


@pytest.mark.parametrize("domain", qc.DOMAINS)
def test_theorem2_round_classification_exhaustive(domain):
    quantizer = qc.ROUND[domain]
    for m, n in _pairs(m_lo=2):
        expected = n % m == 0 and (n // m) % 2 == 1
        assert (qc.divergence(quantizer, m, n) == 0) == expected, (domain, m, n)


@pytest.mark.parametrize("domain", qc.DOMAINS)
@pytest.mark.parametrize("n", (1, 2, 3, 4, 6, 8, 24))
def test_m_equal_one_is_always_equivalent(domain, n):
    # R_1 is constant, so the parity condition of Theorem 2 requires m >= 2.
    assert qc.divergence(qc.ROUND[domain], 1, n) == 0
    assert qc.round_equivalent(1, n)


# --- Divergence closed forms ----------------------------------------------------------------


@pytest.mark.parametrize("domain", qc.DOMAINS)
def test_divergence_closed_forms_for_n_greater_than_m(domain):
    quantizer = qc.ROUND[domain]
    for m in range(1, M_MAX + 1):
        for n in range(m + 1, N_MAX + 1):
            assert qc.divergence(quantizer, m, n) == qc.round_divergence_closed_form(m, n, domain), (
                domain, m, n)


@pytest.mark.parametrize("domain", qc.DOMAINS)
def test_divergence_closed_form_for_n_dividing_m(domain):
    quantizer = qc.ROUND[domain]
    for m in range(2, 48):
        for n in range(1, m):
            if m % n == 0:
                assert qc.divergence(quantizer, m, n) == qc.round_divergence_closed_form(m, n, domain), (
                    domain, m, n)


def test_even_ratio_formulas_differ_by_one_half_cell():
    for m, n in ((12, 24), (3, 6), (5, 20), (7, 42)):
        circle = qc.round_divergence_closed_form(m, n, qc.CIRCLE)
        interval = qc.round_divergence_closed_form(m, n, qc.INTERVAL)
        assert circle == F(m, 2 * n)
        assert interval == F(m - 1, 2 * n)
        assert circle - interval == F(1, 2 * n)


def test_unclassified_regime_is_rejected():
    with pytest.raises(ValueError):
        qc.round_divergence_closed_form(5, 3, qc.CIRCLE)


# --- Worked examples and counterexamples of the working paper ------------------------------------


def test_canonical_witnesses_by_domain():
    assert qc.divergence(qc.round_circle, 24, 36) == F(1, 6)
    assert qc.divergence(qc.round_circle, 12, 24) == F(1, 4)
    assert qc.divergence(qc.round_interval, 24, 36) == F(23, 144)
    assert qc.divergence(qc.round_interval, 12, 24) == F(11, 48)


def test_counterexample_divisibility_is_not_enough_for_round():
    # 12 | 24 but the ratio is even.
    assert qc.divergence(qc.round_circle, 12, 24) > 0
    assert qc.divergence(qc.round_interval, 12, 24) > 0


@pytest.mark.parametrize("quantizer", (qc.round_interval, qc.round_circle))
def test_concrete_divergent_points(quantizer):
    x = F(24, 100)
    assert quantizer(2, quantizer(3, x)) != quantizer(2, x)
    y = F(66, 1000)
    assert quantizer(24, quantizer(36, y)) != quantizer(24, y)


@pytest.mark.parametrize("quantizer", (qc.round_interval, qc.round_circle))
def test_path_dependence_witness(quantizer):
    x = F(66, 1000)
    assert qc.compose(quantizer, [36, 12, 24], x) == F(2, 24)
    assert qc.compose(quantizer, [36, 24], x) == F(1, 24)


# --- Addressing hierarchy -----------------------------------------------------------------------


def test_hierarchy_table_values():
    rows = {(r["fine"], r["coarse"]): r for r in qc.hierarchy_table()}
    assert rows[(36, 12)]["consistent"] and rows[(36, 12)]["mu_circle"] == 0
    assert rows[(60, 12)]["consistent"] and rows[(60, 12)]["mu_circle"] == 0
    assert not rows[(24, 12)]["consistent"] and rows[(24, 12)]["mu_circle"] == F(1, 4)
    assert not rows[(36, 24)]["consistent"] and rows[(36, 24)]["mu_circle"] == F(1, 6)
    assert not rows[(256, 64)]["consistent"] and rows[(256, 64)]["mu_circle"] == F(1, 8)
    assert rows[(192, 64)]["consistent"] and rows[(192, 64)]["mu_circle"] == 0


@pytest.mark.parametrize("bad", (0, -1, 2.0, True))
def test_invalid_grid_is_rejected(bad):
    with pytest.raises(ValueError):
        qc.round_circle(bad, F(1, 3))


# --- Audit of 2026-10-21: counterexamples, pointwise equality, cell formula ----------------------


def test_counterexamples_to_paper_interval_formulas():
    # Paper (v1.0) states these for the interval; the stated values are circle values.
    assert qc.divergence(qc.round_interval, 2, 4) == F(1, 8)      # paper: m/(2n) = 1/4
    assert qc.divergence(qc.round_interval, 2, 3) == F(1, 12)     # sum to j = m-1 gives 1/6
    assert sum(qc._edge_distances(2, 3), F(0)) == F(1, 6)
    assert qc.divergence(qc.round_interval, 2, 1) == F(3, 4)      # paper: 1 - n/m = 1/2


def test_sum_of_distances_is_not_valid_in_general_for_n_less_than_m():
    assert qc.divergence(qc.round_circle, 5, 2) == F(3, 5)
    assert sum(qc._edge_distances(5, 2), F(0)) == F(13, 20)


@pytest.mark.parametrize("domain", qc.DOMAINS)
def test_odd_ratio_equality_is_pointwise(domain):
    quantizer = qc.ROUND[domain]
    for m in range(2, 13):
        for n in range(m, 61, 2 * m):  # n = m, 3m, 5m, ...
            pts = {F(k, 2 * g) for g in (m, n) for k in range(2 * g)}
            ordered = sorted(pts)
            pts |= {(a + b) / 2 for a, b in zip(ordered, ordered[1:])}
            for x in pts:
                assert quantizer(m, quantizer(n, x)) == quantizer(m, x), (domain, m, n, x)


def test_circle_exceeds_interval_by_d0_when_n_greater_than_m():
    for m in range(2, 17):
        for n in range(m + 1, 49):
            diff = qc.divergence(qc.round_circle, m, n) - qc.divergence(qc.round_interval, m, n)
            assert diff == qc._edge_distances(m, n)[0], (m, n)


def test_reflection_commutes_on_circle_but_not_on_interval():
    def reflect(x):
        return (-x) % 1

    def defect(quantizer, n):
        pts = sorted({F(k, 2 * n) for k in range(2 * n + 1)})
        return sum((b - a for a, b in zip(pts, pts[1:])
                    if reflect(quantizer(n, (a + b) / 2)) != quantizer(n, reflect((a + b) / 2))), F(0))

    assert reflect(qc.round_interval(2, F(1, 8))) == 0
    assert qc.round_interval(2, reflect(F(1, 8))) == F(1, 2)
    for n in range(2, 13):
        assert defect(qc.round_interval, n) == F(1, n)
        assert defect(qc.round_circle, n) == 0


@pytest.mark.parametrize("split_cap", (False, True))
@pytest.mark.parametrize("domain", qc.DOMAINS)
def test_cell_formula_matches_exact_divergence(domain, split_cap):
    quantizer = qc.ROUND[domain]
    for m in range(1, 17):
        for n in range(1, 49):
            assert qc.divergence_by_cells(m, n, domain, split_cap) == qc.divergence(quantizer, m, n), (
                domain, split_cap, m, n)


def test_cell_formula_clamp_case_m10_n2():
    # Reviewer's case: with the cap piece [3/4, 1) as its own cell (image 1/2),
    # the unclamped right term would give 1 - 11/20 = 9/20 > 1/4.
    assert qc.divergence(qc.round_interval, 10, 2) == F(17, 20)
    assert qc.divergence_by_cells(10, 2, qc.INTERVAL) == F(17, 20)
    assert qc.divergence_by_cells(10, 2, qc.INTERVAL, split_cap=True) == F(17, 20)


def test_hierarchy_pairs_not_previously_asserted():
    rows = {(r["fine"], r["coarse"]): r for r in qc.hierarchy_table()}
    assert not rows[(48, 12)]["consistent"] and rows[(48, 12)]["mu_circle"] == F(1, 8)
    assert not rows[(18, 12)]["consistent"] and rows[(18, 12)]["mu_circle"] == F(1, 6)
    assert rows[(72, 24)]["consistent"] and rows[(72, 24)]["mu_circle"] == 0
