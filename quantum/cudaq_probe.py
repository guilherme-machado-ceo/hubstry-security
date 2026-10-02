"""Optional NVIDIA CUDA-Q probe for the harmonic-state hypothesis."""
from __future__ import annotations
import math

def sample_harmonic_qubit(theta: float, shots: int = 1000) -> dict:
    """Run a one-qubit harmonic-phase circuit through CUDA-Q."""
    try:
        import cudaq
    except ImportError as exc:
        raise RuntimeError(
            "CUDA-Q is not installed. Install it in an NVIDIA-capable "
            "environment or keep using the NumPy baseline."
        ) from exc

    @cudaq.kernel
    def circuit(angle: float):
        q = cudaq.qubit()
        cudaq.ry(angle, q)
        cudaq.rz(angle, q)
        cudaq.mz(q)

    counts = cudaq.sample(circuit, theta, shots_count=shots)
    return {str(k): int(v) for k, v in counts.items()}

def harmonic_grid(shots: int = 1000) -> list[dict]:
    rows = []
    for k in range(12):
        theta = 2.0 * math.pi * k / 12.0
        rows.append({
            "index": k,
            "theta": theta,
            "counts": sample_harmonic_qubit(theta, shots=shots),
        })
    return rows

if __name__ == "__main__":
    for row in harmonic_grid(shots=256):
        print(row)
