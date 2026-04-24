"""
Quantum Significance Profiles and Consistency Projection
=========================================================

Implements quantum significance profiles over the 64-profile Boolean
lattice, including the consistency projection operator:

    P_C = sum_{sigma in Sigma_C} |sigma><sigma|

where Sigma_C is the set of 7 consistent profiles. This projection
maps any quantum state onto the consistent subspace, enabling
anomaly detection through measurement of the projected amplitude.

Also computes entanglement measures and quantum distinguishability
metrics for profile analysis.

Reference:
    Paper 2 (CC BY 4.0): DOI 10.5281/zenodo.18776462
    pi*sqrt(f(A)) + Quantum - Consistency projection and entanglement.

Author: Hubstry Deep Tech (guilhermemachado.ceo@hubstry.dev)
License: CC BY-NC-SA 4.0
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional

import numpy as np
from numpy.typing import NDArray


@dataclass
class ConsistencyProjectionResult:
    """
    Result of applying the consistency projection P_C to a state.

    Attributes:
        original_state: Input state vector.
        projected_state: State after applying P_C.
        projection_norm: Norm of the projected state.
        consistency_probability: |P_C|psi>|^2 probability of measuring
            a consistent outcome.
        original_label: Label of the input state.
    """

    original_state: NDArray[np.complex128]
    projected_state: NDArray[np.complex128]
    projection_norm: float
    consistency_probability: float
    original_label: str = ""

    @property
    def is_consistent(self) -> bool:
        """Check if the state is entirely in the consistent subspace."""
        return self.consistency_probability > 0.999

    @property
    def anomaly_score(self) -> float:
        """Anomaly score: 1.0 minus consistency probability."""
        return 1.0 - self.consistency_probability


@dataclass
class EntanglementResult:
    """
    Result of entanglement analysis between state partitions.

    Attributes:
        von_neumann_entropy: Entanglement entropy of the reduced state.
        purity: Purity Tr(rho^2) of the reduced state.
        concurrence: Concurrence measure (for 2-qubit partitions).
        linear_entropy: Linear entropy S_L = 1 - Tr(rho^2).
    """

    von_neumann_entropy: float
    purity: float
    concurrence: float
    linear_entropy: float


class ConsistencyProjector:
    """
    Consistency projection operator for the 64-profile lattice.

    Implements the projection:
        P_C = sum_{sigma in Sigma_C} |sigma><sigma|

    where Sigma_C = {0, 1, 2, 4, 8, 16, 32} are the 7 consistent
    profile indices.

    Reference:
        Paper 2 (CC BY 4.0): DOI 10.5281/zenodo.18776462
        Consistency projection P_C over Sigma_C.
    """

    CONSISTENT_INDICES = [0, 1, 2, 4, 8, 16, 32]
    DIM = 64

    def __init__(self) -> None:
        self._projection_matrix = self._build_projection_matrix()

    def _build_projection_matrix(self) -> NDArray[np.complex128]:
        """
        Build the 64x64 consistency projection matrix.

        P_C[i,j] = 1 if i == j and i in Sigma_C, else 0.

        Returns:
            64x64 complex projection matrix.
        """
        P = np.zeros((self.DIM, self.DIM), dtype=np.complex128)
        for idx in self.CONSISTENT_INDICES:
            P[idx, idx] = 1.0 + 0j
        return P

    def project(
        self,
        state: NDArray[np.complex128],
    ) -> ConsistencyProjectionResult:
        """
        Apply the consistency projection to a quantum state.

        P_C |psi> = sum_{sigma in Sigma_C} <sigma|psi> |sigma>

        Args:
            state: 64-dimensional complex state vector.

        Returns:
            ConsistencyProjectionResult with projection details.
        """
        projected = self._projection_matrix @ state
        proj_norm = float(np.linalg.norm(projected))
        orig_norm_sq = float(np.real(np.vdot(state, state)))
        if orig_norm_sq > 0:
            consistency_prob = (proj_norm ** 2) / orig_norm_sq
        else:
            consistency_prob = 0.0

        return ConsistencyProjectionResult(
            original_state=state.copy(),
            projected_state=projected,
            projection_norm=proj_norm,
            consistency_probability=min(1.0, consistency_prob),
        )

    def project_from_amplitudes(
        self,
        amplitudes: list[float],
        label: str = "",
    ) -> ConsistencyProjectionResult:
        """
        Convenience: project from a list of real amplitudes.

        Args:
            amplitudes: 64 real amplitude values.
            label: Label for the state.

        Returns:
            ConsistencyProjectionResult.
        """
        state = np.array(amplitudes, dtype=np.complex128)
        result = self.project(state)
        result.original_label = label
        return result


class QuantumProfileAnalyzer:
    """
    Analyzer for quantum significance profiles over the 64-profile lattice.

    Combines the consistency projection with entanglement measures
    and distinguishability analysis to provide a comprehensive view
    of the quantum security properties of profile states.

    Attributes:
        projector: Consistency projection operator.
        dim: Hilbert space dimension (64).
    """

    def __init__(self) -> None:
        self.projector = ConsistencyProjector()
        self.dim = self.projector.DIM

    def create_profile_state(
        self,
        profile_bits: int,
        amplitude: float = 1.0,
    ) -> NDArray[np.complex128]:
        """
        Create a quantum state concentrated on a single profile.

        Args:
            profile_bits: Profile bitmask (0 to 63).
            amplitude: Complex amplitude for the profile.

        Returns:
            64-dimensional state vector.
        """
        state = np.zeros(self.dim, dtype=np.complex128)
        state[profile_bits] = complex(amplitude)
        return state

    def create_superposition(
        self,
        indices: list[int],
        amplitudes: Optional[list[float]] = None,
    ) -> NDArray[np.complex128]:
        """
        Create a superposition over specified profile indices.

        Args:
            indices: List of profile indices.
            amplitudes: Optional amplitude list (uniform if None).

        Returns:
            Normalized 64-dimensional state vector.
        """
        state = np.zeros(self.dim, dtype=np.complex128)
        if amplitudes is None:
            amplitudes = [1.0] * len(indices)
        for idx, amp in zip(indices, amplitudes):
            state[idx] = complex(amp)
        norm = np.linalg.norm(state)
        if norm > 0:
            state /= norm
        return state

    def compute_entanglement(
        self,
        state: NDArray[np.complex128],
        partition_qubits: int = 3,
    ) -> EntanglementResult:
        """
        Compute entanglement measures for a bipartition.

        Traces out the first `partition_qubits` qubits to obtain
        the reduced density matrix, then computes entropy-based
        entanglement measures.

        Args:
            state: 64-dimensional state vector (6 qubits).
            partition_qubits: Number of qubits to trace out (default 3).

        Returns:
            EntanglementResult with computed measures.
        """
        dims_keep = 1 << (6 - partition_qubits)
        dims_trace = 1 << partition_qubits
        reshaped = state.reshape(dims_trace, dims_keep)
        rho_partial = reshaped @ reshaped.conj().T
        rho_reduced = rho_partial / np.trace(rho_partial)

        eigenvalues = np.linalg.eigvalsh(rho_reduced)
        eigenvalues = np.maximum(eigenvalues, 0)
        eigenvalues /= np.sum(eigenvalues)

        entropy = 0.0
        for ev in eigenvalues:
            if ev > 1e-12:
                entropy -= ev * math.log2(ev)

        purity = float(np.real(np.trace(rho_reduced @ rho_reduced)))
        linear_entropy = 1.0 - purity

        concurrence = min(linear_entropy, 1.0)

        return EntanglementResult(
            von_neumann_entropy=entropy,
            purity=purity,
            concurrence=concurrence,
            linear_entropy=linear_entropy,
        )

    def analyze_profile(
        self,
        state: NDArray[np.complex128],
        label: str = "",
    ) -> dict:
        """
        Perform full quantum profile analysis.

        Combines consistency projection and entanglement analysis
        into a single comprehensive report.

        Args:
            state: 64-dimensional quantum state vector.
            label: Human-readable label for the state.

        Returns:
            Dictionary with all analysis results.
        """
        proj_result = self.projector.project(state)
        proj_result.original_label = label

        ent_result = self.compute_entanglement(state)

        return {
            "label": label,
            "consistency_probability": proj_result.consistency_probability,
            "anomaly_score": proj_result.anomaly_score,
            "is_consistent": proj_result.is_consistent,
            "projection_norm": proj_result.projection_norm,
            "entanglement_entropy": ent_result.von_neumann_entropy,
            "purity": ent_result.purity,
            "concurrence": ent_result.concurrence,
            "linear_entropy": ent_result.linear_entropy,
            "security_assessment": self._assess_security(
                proj_result, ent_result
            ),
        }

    def _assess_security(
        self,
        proj: ConsistencyProjectionResult,
        ent: EntanglementResult,
    ) -> str:
        """Classify overall security based on consistency and entanglement."""
        if proj.consistency_probability > 0.95 and ent.purity > 0.9:
            return "SECURE"
        if proj.consistency_probability > 0.80 and ent.purity > 0.7:
            return "MODERATE"
        if proj.consistency_probability > 0.50:
            return "WEAK"
        return "VULNERABLE"

    def batch_analyze(
        self,
        states: list[tuple[NDArray[np.complex128], str]],
    ) -> list[dict]:
        """Analyze multiple states and return a list of reports."""
        return [self.analyze_profile(s, l) for s, l in states]


def simulate_quantum_profiles() -> None:
    """Demonstrate quantum profile analysis with consistency projection."""
    print("=" * 60)
    print("  Quantum Significance Profiles - Consistency Projection")
    print("  Reference: DOI 10.5281/zenodo.18776462")
    print("  P_C = sum_{sigma in Sigma_C} |sigma><sigma|")
    print("=" * 60)

    analyzer = QuantumProfileAnalyzer()

    print(f"\n  Consistent indices: {ConsistencyProjector.CONSISTENT_INDICES}")
    print(f"  Projection matrix shape: {analyzer.projector._projection_matrix.shape}")
    print(f"  Projection rank: {int(np.trace(analyzer.projector._projection_matrix))}")

    test_cases: list[tuple[NDArray[np.complex128], str]] = [
        (
            analyzer.create_profile_state(0, 1.0),
            "|000000> (consistent)",
        ),
        (
            analyzer.create_profile_state(1, 1.0),
            "|000001> (consistent)",
        ),
        (
            analyzer.create_profile_state(3, 1.0),
            "|000011> (inconsistent)",
        ),
        (
            analyzer.create_profile_state(63, 1.0),
            "|111111> (inconsistent)",
        ),
        (
            analyzer.create_superposition([0, 1, 2, 4, 8, 16, 32]),
            "Uniform over consistent set",
        ),
        (
            analyzer.create_superposition(list(range(64))),
            "Uniform over all 64 profiles",
        ),
        (
            analyzer.create_superposition([0, 63], [0.7, 0.3]),
            "Superposition |000000> + 0.43|111111>",
        ),
    ]

    print(
        f"\n  {'Label':>35}  {'Cons_Prob':>10}  "
        f"{'Anomaly':>8}  {'Entropy':>8}  {'Purity':>8}  {'Status':>12}"
    )
    print(
        f"  {'-'*35}  {'-'*10}  {'-'*8}  {'-'*8}  {'-'*8}  {'-'*12}"
    )

    for state, label in test_cases:
        report = analyzer.analyze_profile(state, label)
        print(
            f"  {report['label']:>35}  "
            f"{report['consistency_probability']:>10.4f}  "
            f"{report['anomaly_score']:>8.4f}  "
            f"{report['entanglement_entropy']:>8.4f}  "
            f"{report['purity']:>8.4f}  "
            f"{report['security_assessment']:>12}"
        )

    print(f"\n  --- Detailed Consistent State Analysis ---")
    for idx in ConsistencyProjector.CONSISTENT_INDICES:
        state = analyzer.create_profile_state(idx, 1.0)
        result = analyzer.projector.project(state)
        ent = analyzer.compute_entanglement(state)
        print(
            f"  Profile {format(idx, '06b')}: "
            f"P_C|psi> norm={result.projection_norm:.4f}, "
            f"cons_prob={result.consistency_probability:.4f}, "
            f"entropy={ent.von_neumann_entropy:.4f}"
        )

    print("=" * 60)


if __name__ == "__main__":
    simulate_quantum_profiles()