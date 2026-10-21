"""
quantum/quantizer_composition.py — Composition of uniform quantizers
=====================================================================

Exact (rational) verification of the theory of quantizer composition and its
use as an addressing-hierarchy rule for HALE-Q phase grids. Pure Python,
``fractions.Fraction``; no floating point in any decision.

Objects (n >= 1):
  Floor   Q_n(x) = floor(n x) / n                         on [0, 1)
  Round   R_n(x) = round-half-up(n x) / n, two domains:
          - INTERVAL [0, 1): results capped at (n-1)/n so the map stays in [0, 1);
          - CIRCLE  R/Z:    results taken mod 1 (phase grids, theta = 2*pi*x).

Divergence: mu(m, n) = Lebesgue measure of {x : A_m(A_n(x)) != A_m(x)}.

Results verified exhaustively over finite ranges in tests/test_quantizer_composition.py:
  Theorem 1 (floor):  Q_m o Q_n = Q_m pointwise  <=>  m | n.
  Theorem 2 (round, both domains, m >= 2):  R_m o R_n = R_m a.e.  <=>  n/m odd integer.
            For m = 1, R_1 is constant, so R_1 o R_n = R_1 for every n.
  Divergence for n > m, q = n/m (round):
            q odd integer      CIRCLE 0          INTERVAL 0
            q even integer     CIRCLE m/(2n)     INTERVAL (m-1)/(2n)
            q not integer      CIRCLE sum_{j=0}^{m-1} d_j
                               INTERVAL sum_{j=0}^{m-2} d_j
            where d_j is the distance from b_j = (j+1/2)/m to the nearest
            Voronoi edge (k+1/2)/n of R_n.
  Divergence for n | m, n < m (round):
            CIRCLE 1 - n/m     INTERVAL 1 - n/m + 1/(2m)

Addressing reading: a HALE-Q address read on a fine phase grid n and then
re-read on a coarse grid m by nearest-point rounding is consistent with a
direct coarse reading iff n/m is an odd integer; mu is the fraction of
phases that land on a different coarse address.

Classification (project governance):
  The theorems are mathematical results of the source working paper; this
  module provides exact computational verification over finite ranges,
  which is regression evidence, not a general proof.
  No security, hardness or quantum claim is made.

Run:
    python -m quantum.quantizer_composition      (from repository root)

Author: Hubstry Deep Tech (guilhermemachado.ceo@hubstry.dev)
License: CC BY-NC-SA 4.0
"""

from __future__ import annotations

import math
from fractions import Fraction
from typing import Callable

INTERVAL = "interval"
CIRCLE = "circle"
DOMAINS = (INTERVAL, CIRCLE)

Quantizer = Callable[[int, Fraction], Fraction]


def _check(n: int) -> None:
    if not isinstance(n, int) or isinstance(n, bool) or n < 1:
        raise ValueError("grid size must be a positive integer")


def floor_q(n: int, x: Fraction) -> Fraction:
    """Floor quantizer Q_n on [0, 1)."""
    _check(n)
    return Fraction(math.floor(n * x), n)


def round_interval(n: int, x: Fraction) -> Fraction:
    """Round-half-up quantizer R_n on [0, 1), capped at (n-1)/n."""
    _check(n)
    return Fraction(min(math.floor(n * x + Fraction(1, 2)), n - 1), n)


def round_circle(n: int, x: Fraction) -> Fraction:
    """Round-half-up quantizer R_n on the circle R/Z (result mod 1)."""
    _check(n)
    return Fraction(math.floor(n * x + Fraction(1, 2)) % n, n)


ROUND: dict[str, Quantizer] = {INTERVAL: round_interval, CIRCLE: round_circle}


def compose(quantizer: Quantizer, grids: list[int], x: Fraction) -> Fraction:
    """Apply a chain of quantizers; grids are applied left to right (first = innermost)."""
    for n in grids:
        x = quantizer(n, x)
    return x


def divergence(quantizer: Quantizer, m: int, n: int) -> Fraction:
    """Exact measure of {x in [0,1) : A_m(A_n(x)) != A_m(x)}.

    Both maps are constant between consecutive multiples of 1/(2m) and
    1/(2n), so evaluating at the midpoint of each piece is exact.
    """
    _check(m)
    _check(n)
    points = {Fraction(0), Fraction(1)}
    for g in (m, n):
        points.update(Fraction(k, 2 * g) for k in range(2 * g + 1))
    ordered = sorted(points)
    total = Fraction(0)
    for a, b in zip(ordered, ordered[1:]):
        mid = (a + b) / 2
        if quantizer(m, quantizer(n, mid)) != quantizer(m, mid):
            total += b - a
    return total


# ---------------------------------------------------------------------------
# Closed forms
# ---------------------------------------------------------------------------


def _edge_distances(m: int, n: int) -> list[Fraction]:
    """d_j: distance from each boundary b_j of R_m to the nearest Voronoi edge of R_n."""
    edges = [Fraction(2 * k + 1, 2 * n) for k in range(-1, n + 1)]
    return [min(abs(Fraction(2 * j + 1, 2 * m) - e) for e in edges) for j in range(m)]


def round_divergence_closed_form(m: int, n: int, domain: str) -> Fraction:
    """Closed-form divergence of R_m o R_n versus R_m.

    Covers n > m (all ratios) and n | m with n < m. Raises ValueError for
    the unclassified regime (n < m with n not dividing m).
    """
    _check(m)
    _check(n)
    if domain not in DOMAINS:
        raise ValueError("domain must be 'interval' or 'circle'")
    if m == 1:
        return Fraction(0)
    if n == m:
        return Fraction(0)
    if n > m:
        if n % m == 0:
            q = n // m
            if q % 2 == 1:
                return Fraction(0)
            return Fraction(m, 2 * n) if domain == CIRCLE else Fraction(m - 1, 2 * n)
        d = _edge_distances(m, n)
        return sum(d, Fraction(0)) if domain == CIRCLE else sum(d[:-1], Fraction(0))
    if m % n == 0:
        base = 1 - Fraction(n, m)
        return base if domain == CIRCLE else base + Fraction(1, 2 * m)
    raise ValueError("n < m with n not dividing m is not classified")


def round_equivalent(m: int, n: int) -> bool:
    """Theorem 2: R_m o R_n = R_m a.e. (either domain)."""
    _check(m)
    _check(n)
    if m == 1:
        return True
    return n % m == 0 and (n // m) % 2 == 1


def floor_equivalent(m: int, n: int) -> bool:
    """Theorem 1: Q_m o Q_n = Q_m pointwise."""
    _check(m)
    _check(n)
    return n % m == 0


# ---------------------------------------------------------------------------
# Addressing-hierarchy report
# ---------------------------------------------------------------------------

HIERARCHY_PAIRS: tuple[tuple[int, int], ...] = (
    (36, 12), (60, 12), (24, 12), (48, 12), (36, 24), (18, 12), (72, 24), (256, 64), (192, 64),
)


def hierarchy_table(pairs: tuple[tuple[int, int], ...] = HIERARCHY_PAIRS) -> list[dict]:
    rows = []
    for fine, coarse in pairs:
        mu = divergence(round_circle, coarse, fine)
        rows.append(
            {
                "fine": fine,
                "coarse": coarse,
                "ratio": Fraction(fine, coarse),
                "consistent": round_equivalent(coarse, fine),
                "mu_circle": mu,
            }
        )
    return rows


def main() -> None:
    print("HALE-Q addressing hierarchy: fine grid -> coarse grid by nearest point (circle)")
    print(f"{'fine':>5} {'coarse':>6} {'ratio':>7} {'consistent':>10} {'mu':>8}")
    for r in hierarchy_table():
        print(f"{r['fine']:>5} {r['coarse']:>6} {str(r['ratio']):>7} "
              f"{str(r['consistent']):>10} {str(r['mu_circle']):>8}")


if __name__ == "__main__":
    main()
