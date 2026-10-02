# Quantum Research Track

This directory turns the HALE/HSL harmonic hypothesis into a measurable
quantum-information experiment without claiming that the current prototype
is quantum-secure.

The first experiment maps a harmonic phase

    theta_k = 2*pi*k/n

to a normalized qubit state

    |psi(theta)> = cos(theta/2)|0> + exp(i*theta) sin(theta/2)|1>.

We measure fidelity and phase distance between states.

## Research question

The original hypothesis is that harmonic subdivision has no natural terminal
scale. That does NOT imply that the harmonic series automatically becomes
quantum.

The testable question is whether the harmonic parameterization produces
useful invariants in a quantum state space, such as distinguishability,
robustness under perturbation, collision behavior, anomaly sensitivity, and
scaling from n=12 to larger subdivisions.

## NVIDIA path

NVIDIA CUDA-Q is the preferred optional backend because Hubstry is a member
of NVIDIA Inception. CUDA-Q provides a Python programming model for hybrid
CPU/GPU/QPU workflows and GPU-accelerated quantum simulation.

Run the CPU baseline first:

    python -m quantum.harmonic_state

In an NVIDIA-capable environment:

    pip install cudaq
    python -m quantum.cudaq_probe

For larger simulations, NVIDIA cuQuantum provides GPU-accelerated
state-vector and tensor-network simulation.

## PQC path

Do not replace NIST cryptography with the harmonic construction.

Near-term architecture:

    HALE/HSL context
          |
          +---- ML-KEM (FIPS 203) ---- session key
          |
          +---- ML-DSA (FIPS 204) ---- authentication
          |
          +---- harmonic/quantum research ---- identity/segmentation signal

NVIDIA cuPQC is a later acceleration target. It provides GPU implementations
of ML-KEM and ML-DSA; first establish a correct standardized CPU baseline,
then benchmark GPU acceleration.

## Reproducibility

Record subdivision n, phase index k, fidelity, perturbation, false-accept /
false-reject behavior, CPU/GPU runtime, memory, backend and version.

No security claim should be made from simulation alone.
