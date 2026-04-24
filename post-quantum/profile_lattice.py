"""
64-Profile Boolean Lattice with Consistency Checking
=====================================================

Implements the 64-profile Boolean lattice structure isomorphic to
the 6-qubit computational basis. Out of 64 possible profiles,
exactly 7 are classified as "consistent" according to the
consistency criteria from Paper 2.

Each profile is a 6-bit vector representing a truth assignment
to 6 Boolean variables, forming a lattice under bitwise
subset inclusion.

Reference:
    Paper 2 (CC BY 4.0): DOI 10.5281/zenodo.18776462
    pi*sqrt(f(A)) + Quantum - 64-profile lattice, 7 consistent profiles.

Author: Hubstry Deep Tech (guilhermemachado.ceo@hubstry.dev)
License: CC BY-NC-SA 4.0
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import FrozenSet, Iterator, Optional

import numpy as np
from numpy.typing import NDArray


@dataclass(frozen=True)
class BooleanProfile:
    """
    A 6-bit Boolean profile in the 64-profile lattice.

    Each profile is a frozen bitmask where bit i represents
    the truth value of variable x_i. The profile |p> maps
    to the computational basis state |p> in the 6-qubit space.

    Attributes:
        bits: Integer bitmask (0 to 63).
        label: Human-readable label (e.g., "010011").
    """

    bits: int
    label: str = ""

    def __post_init__(self) -> None:
        if not (0 <= self.bits < 64):
            raise ValueError(f"bits must be in [0, 63], got {self.bits}")
        if not self.label:
            object.__setattr__(
                self,
                "label",
                format(self.bits, "06b"),
            )

    @property
    def n_bits(self) -> int:
        """Number of set bits (population count)."""
        return bin(self.bits).count("1")

    @property
    def as_tuple(self) -> tuple[int, ...]:
        """Profile as a tuple of 6 bits (MSB first)."""
        return tuple(int(b) for b in self.label)

    @property
    def as_array(self) -> NDArray[np.int8]:
        """Profile as a numpy int8 array of shape (6,)."""
        return np.array(self.as_tuple, dtype=np.int8)

    def hamming_distance(self, other: "BooleanProfile") -> int:
        """Compute Hamming distance to another profile."""
        xor = self.bits ^ other.bits
        return bin(xor).count("1")

    def is_subset_of(self, other: "BooleanProfile") -> bool:
        """Check if this profile is a subset (bitwise) of another."""
        return (self.bits & other.bits) == self.bits

    def is_superset_of(self, other: "BooleanProfile") -> bool:
        """Check if this profile is a superset (bitwise) of another."""
        return (self.bits | other.bits) == self.bits

    def meet(self, other: "BooleanProfile") -> "BooleanProfile":
        """Compute the lattice meet (bitwise AND)."""
        return BooleanProfile(self.bits & other.bits)

    def join(self, other: "BooleanProfile") -> "BooleanProfile":
        """Compute the lattice join (bitwise OR)."""
        return BooleanProfile(self.bits | other.bits)

    def __repr__(self) -> str:
        return f"BooleanProfile({self.label})"


class ProfileLattice:
    """
    The complete 64-profile Boolean lattice.

    The lattice L = {0, 1}^6 has 2^6 = 64 profiles, isomorphic
    to the 6-qubit computational basis. The partial order is
    bitwise inclusion: p <= q iff p & q == p.

    Reference:
        Paper 2 (CC BY 4.0): DOI 10.5281/zenodo.18776462
        64-profile lattice isomorphic to 6-qubit basis.

    Attributes:
        profiles: Dict mapping bitmask to BooleanProfile.
        consistent_profiles: Set of the 7 consistent profiles.
    """

    N_VARIABLES = 6
    N_PROFILES = 64

    def __init__(self) -> None:
        self.profiles: dict[int, BooleanProfile] = {
            i: BooleanProfile(bits=i) for i in range(self.N_PROFILES)
        }
        self._build_consistency_set()

    def _build_consistency_set(self) -> None:
        """
        Build the set of 7 consistent profiles.

        A profile p is consistent if it satisfies the harmonic
        consistency constraint from Paper 2: the truth assignment
        must not create logical contradictions with the HALE
        structural equations.

        The 7 consistent profiles (in binary notation):
            000000, 000001, 000010, 000100, 001000, 010000, 100000

        These correspond to the singleton and empty assignments,
        representing profiles with at most one variable asserted.
        """
        self._consistent_bits = {0, 1, 2, 4, 8, 16, 32}
        self.consistent_profiles: set[BooleanProfile] = {
            self.profiles[b] for b in self._consistent_bits
        }

    def is_consistent(self, profile: BooleanProfile) -> bool:
        """Check if a profile is in the consistent set."""
        return profile.bits in self._consistent_bits

    def get_consistent_profiles(self) -> list[BooleanProfile]:
        """Return sorted list of all 7 consistent profiles."""
        return sorted(
            self.consistent_profiles, key=lambda p: p.bits
        )

    def get_inconsistent_profiles(self) -> list[BooleanProfile]:
        """Return sorted list of all 57 inconsistent profiles."""
        return sorted(
            [
                p
                for p in self.profiles.values()
                if not self.is_consistent(p)
            ],
            key=lambda p: p.bits,
        )

    def consistency_ratio(self) -> float:
        """Compute the ratio of consistent to total profiles."""
        return len(self.consistent_profiles) / self.N_PROFILES

    def upper_neighbors(self, profile: BooleanProfile) -> list[BooleanProfile]:
        """Return profiles directly above the given profile in the lattice."""
        result: list[BooleanProfile] = []
        for i in range(self.N_VARIABLES):
            bit = 1 << i
            if not (profile.bits & bit):
                neighbor = self.profiles[profile.bits | bit]
                result.append(neighbor)
        return result

    def lower_neighbors(self, profile: BooleanProfile) -> list[BooleanProfile]:
        """Return profiles directly below the given profile in the lattice."""
        result: list[BooleanProfile] = []
        for i in range(self.N_VARIABLES):
            bit = 1 << i
            if profile.bits & bit:
                neighbor = self.profiles[profile.bits ^ bit]
                result.append(neighbor)
        return result

    def rank(self, profile: BooleanProfile) -> int:
        """Compute the lattice rank (number of set bits)."""
        return profile.n_bits

    def distance_matrix(self) -> NDArray[np.int32]:
        """
        Compute the full 64x64 Hamming distance matrix.

        Returns:
            numpy array of shape (64, 64) with integer distances.
        """
        n = self.N_PROFILES
        mat = np.zeros((n, n), dtype=np.int32)
        for i in range(n):
            for j in range(n):
                mat[i, j] = self.profiles[i].hamming_distance(
                    self.profiles[j]
                )
        return mat

    def detect_anomaly(self, profile: BooleanProfile) -> dict:
        """
        Analyze a profile for anomaly indicators.

        An anomaly is detected when:
        1. The profile is inconsistent (not in the 7 consistent set)
        2. The profile has high Hamming weight (> 1 for strict consistency)
        3. The profile is far from all consistent profiles

        Args:
            profile: The profile to analyze.

        Returns:
            Dictionary with anomaly analysis results.
        """
        is_cons = self.is_consistent(profile)
        min_dist = min(
            profile.hamming_distance(cp)
            for cp in self.consistent_profiles
        )
        closest_consistent = min(
            self.consistent_profiles,
            key=lambda cp: profile.hamming_distance(cp),
        )
        anomaly_score = (6 - min_dist) / 6.0 if not is_cons else 0.0

        return {
            "profile": profile.label,
            "is_consistent": is_cons,
            "hamming_weight": profile.n_bits,
            "min_distance_to_consistent": min_dist,
            "closest_consistent": closest_consistent.label,
            "anomaly_score": anomaly_score,
            "is_anomaly": not is_cons,
        }

    def lattice_histogram(self) -> NDArray[np.int32]:
        """
        Count profiles at each rank level.

        Returns:
            Array of length 7 (ranks 0 through 6) with profile counts.
        """
        hist = np.zeros(self.N_VARIABLES + 1, dtype=np.int32)
        for p in self.profiles.values():
            hist[p.n_bits] += 1
        return hist


def simulate_profile_lattice() -> None:
    """Demonstrate the 64-profile lattice and consistency analysis."""
    print("=" * 60)
    print("  64-Profile Boolean Lattice - Consistency Analysis")
    print("  Reference: DOI 10.5281/zenodo.18776462")
    print("  7 consistent profiles out of 64 total")
    print("=" * 60)

    lattice = ProfileLattice()

    consistent = lattice.get_consistent_profiles()
    print(f"\n  Consistent profiles ({len(consistent)}):")
    for p in consistent:
        print(f"    {p.label} (bits={p.bits}, weight={p.n_bits})")

    print(f"\n  Consistency ratio: {lattice.consistency_ratio():.4f}")
    print(f"  Inconsistent profiles: {64 - len(consistent)}")

    hist = lattice.lattice_histogram()
    print(f"\n  Lattice histogram (rank distribution):")
    for rank, count in enumerate(hist):
        bar = "#" * int(count / 2)
        print(f"    Rank {rank}: {count:>3}  {bar}")

    print(f"\n  --- Anomaly Detection Examples ---")
    test_profiles = [0, 1, 3, 7, 15, 31, 63]
    for bits in test_profiles:
        p = lattice.profiles[bits]
        analysis = lattice.detect_anomaly(p)
        status = "CONSISTENT" if not analysis["is_anomaly"] else "ANOMALY"
        print(
            f"  {analysis['profile']} -> {status} "
            f"(score={analysis['anomaly_score']:.2f}, "
            f"closest={analysis['closest_consistent']}, "
            f"dist={analysis['min_distance_to_consistent']})"
        )

    print(f"\n  --- Lattice Operations Demo ---")
    p1 = lattice.profiles[5]
    p2 = lattice.profiles[9]
    meet = p1.meet(p2)
    join = p1.join(p2)
    print(f"  {p1.label} AND {p2.label} = {meet.label}")
    print(f"  {p1.label} OR  {p2.label} = {join.label}")
    print(f"  Hamming distance:     {p1.hamming_distance(p2)}")
    print("=" * 60)


if __name__ == "__main__":
    simulate_profile_lattice()