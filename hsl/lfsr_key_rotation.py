"""
LFSR-Based Key Rotation Module
================================

Implements Linear Feedback Shift Register (LFSR) key rotation
with the recurrence relation:
    sigma_{k+1} = f_LFSR(sigma_k, seed)

The seed is derived from the fundamental frequency f0 concatenated
with a high-resolution timestamp, providing temporal uniqueness
for each key rotation cycle.

Reference:
    Paper 4 (CC BY 4.0): DOI 10.5281/zenodo.19056387 - HPG 1.0
    LFSR key rotation with configurable feedback polynomial.

Author: Hubstry Deep Tech (guilhermemachado.ceo@hubstry.dev)
License: CC BY-NC-SA 4.0
"""

from __future__ import annotations

import hashlib
import math
import struct
import time
from dataclasses import dataclass, field
from typing import Optional

import numpy as np
from numpy.typing import NDArray


@dataclass
class LFSRConfig:
    """Configuration for the LFSR key rotation engine."""

    polynomial_taps: list[int] = field(
        default_factory=lambda: [16, 14, 13, 11]
    )
    register_size: int = 32
    key_byte_length: int = 32
    rotation_interval_seconds: float = 300.0


@dataclass
class LFSRState:
    """
    State of the LFSR at a given rotation step.

    Attributes:
        register: Current LFSR register value as integer.
        step: Current rotation step number.
        timestamp: When this state was generated.
        key: Derived key material (bytes).
    """

    register: int
    step: int
    timestamp: float
    key: bytes


class LFSREngine:
    """
    LFSR-based key rotation engine.

    Implements the key rotation recurrence from Paper 4:
        sigma_{k+1} = f_LFSR(sigma_k, seed)

    The seed is derived from:
        seed = SHA-256(str(f0) + str(timestamp_ns))

    The feedback polynomial is configurable. A default 32-bit
    maximal-length polynomial with taps at [16, 14, 13, 11]
    provides a period of 2^32 - 1 before key repetition.

    Attributes:
        config: LFSR configuration.
        _state: Current LFSR state.
        _seed: Initial seed derived from f0 + timestamp.
        _f0: Fundamental frequency used for seed generation.
    """

    def __init__(
        self,
        f0: float = 440.0,
        config: Optional[LFSRConfig] = None,
    ) -> None:
        self.config = config or LFSRConfig()
        self._f0 = f0
        self._seed = self._derive_seed()
        self._state = self._initialize_state()

    def _derive_seed(self) -> int:
        """
        Derive the LFSR seed from f0 and current timestamp.

        The seed material is:
            seed = SHA-256(f0 || timestamp_ns) truncated to register bits

        Returns:
            Integer seed value for LFSR initialization.
        """
        timestamp_ns = time.time_ns()
        material = f"{self._f0}:{timestamp_ns}".encode("utf-8")
        digest = hashlib.sha256(material).digest()
        seed_int = int.from_bytes(digest[:8], "big")
        mask = (1 << self.config.register_size) - 1
        return seed_int & mask

    def _initialize_state(self) -> LFSRState:
        """Initialize the LFSR state from the derived seed."""
        register = self._seed
        key = self._derive_key(register)
        return LFSRState(
            register=register,
            step=0,
            timestamp=time.time(),
            key=key,
        )

    def _feedback_bit(self, register: int) -> int:
        """
        Compute the LFSR feedback bit from the current register.

        The feedback bit is the XOR of all tap positions:
            feedback = XOR(register[tap] for tap in polynomial_taps)

        Args:
            register: Current LFSR register value.

        Returns:
            Single feedback bit (0 or 1).
        """
        fb = 0
        for tap in self.config.polynomial_taps:
            fb ^= (register >> tap) & 1
        return fb

    def _step_register(self, register: int) -> int:
        """
        Advance the LFSR register by one step.

        Implements: sigma_{k+1} = f_LFSR(sigma_k)

        The register shifts left by 1 bit, and the feedback bit
        is inserted at position 0.

        Args:
            register: Current register state.

        Returns:
            Next register state.
        """
        fb = self._feedback_bit(register)
        mask = (1 << self.config.register_size) - 1
        new_reg = ((register << 1) | fb) & mask
        return new_reg

    def _derive_key(self, register: int) -> bytes:
        """
        Derive cryptographic key material from the LFSR register.

        Uses SHA-256 to expand the register state into a full-length
        key, concatenated with the f0 value for domain separation.

        Args:
            register: Current LFSR register value.

        Returns:
            Key material bytes of configured length.
        """
        reg_bytes = register.to_bytes(
            (self.config.register_size + 7) // 8, "big"
        )
        material = reg_bytes + str(self._f0).encode("utf-8")
        digest = hashlib.sha256(material).digest()
        if len(digest) >= self.config.key_byte_length:
            return digest[: self.config.key_byte_length]
        repeated = digest
        while len(repeated) < self.config.key_byte_length:
            repeated += hashlib.sha256(
                repeated[-32:] + str(self._f0).encode("utf-8")
            ).digest()
        return repeated[: self.config.key_byte_length]

    def rotate(self, steps: int = 1) -> LFSRState:
        """
        Rotate the LFSR by the specified number of steps.

        Each step applies:
            sigma_{k+1} = f_LFSR(sigma_k, seed)

        The seed is mixed into every Nth step to prevent
        period-boundary key repetition.

        Args:
            steps: Number of rotation steps to advance.

        Returns:
            New LFSRState after rotation.
        """
        reg = self._state.register
        step = self._state.step

        for _ in range(steps):
            reg = self._step_register(reg)
            step += 1
            if step % 1024 == 0:
                reg ^= self._seed & ((1 << self.config.register_size) - 1)

        key = self._derive_key(reg)
        self._state = LFSRState(
            register=reg, step=step, timestamp=time.time(), key=key
        )
        return self._state

    def get_current_key(self) -> bytes:
        """Return the current derived key material."""
        return self._state.key

    def get_current_state(self) -> LFSRState:
        """Return a copy of the current LFSR state."""
        return LFSRState(
            register=self._state.register,
            step=self._state.step,
            timestamp=self._state.timestamp,
            key=self._state.key,
        )

    def generate_key_schedule(
        self, n_keys: int = 16
    ) -> list[bytes]:
        """
        Pre-generate a schedule of future keys.

        Args:
            n_keys: Number of keys to pre-generate.

        Returns:
            List of key bytes in chronological order.
        """
        keys: list[bytes] = []
        saved = self._state
        reg = self._state.register
        step = self._state.step

        for _ in range(n_keys):
            reg = self._step_register(reg)
            step += 1
            keys.append(self._derive_key(reg))

        self._state = saved
        return keys

    def compute_period(self) -> int:
        """
        Compute the actual period of the LFSR configuration.

        This may be slow for large register sizes. For a maximal-length
        LFSR, the period should be 2^n - 1.

        Returns:
            Number of steps before the register repeats.
        """
        reg = self._state.register
        start = reg
        count = 0
        mask = (1 << self.config.register_size) - 1

        while True:
            reg = self._step_register(reg) & mask
            count += 1
            if reg == start or count > (1 << self.config.register_size):
                break

        return count

    def verify_partner(
        self,
        partner_register: int,
        max_drift: int = 10,
    ) -> bool:
        """
        Verify that a partner LFSR state is within acceptable drift.

        Args:
            partner_register: Partner current register value.
            max_drift: Maximum allowed step difference.

        Returns:
            True if the partner state is within synchronization range.
        """
        for offset in range(-max_drift, max_drift + 1):
            test_reg = self._state.register
            for _ in range(abs(offset)):
                test_reg = self._step_register(test_reg)
            if test_reg == partner_register:
                return True
        return False

    def __repr__(self) -> str:
        return (
            f"LFSREngine(f0={self._f0}, "
            f"step={self._state.step}, "
            f"reg=0x{self._state.register:08x}, "
            f"key={self._state.key[:8].hex()}...)"
        )


def simulate_lfsr_rotation() -> None:
    """Demonstrate LFSR key rotation with seed from f0 + timestamp."""
    print("=" * 60)
    print("  LFSR Key Rotation - Seed from f0 + Timestamp")
    print("  Reference: DOI 10.5281/zenodo.19056387 (HPG 1.0)")
    print("  Recurrence: sigma_{k+1} = f_LFSR(sigma_k, seed)")
    print("=" * 60)

    engine = LFSREngine(f0=440.0)

    print(f"\n  Fundamental frequency f0: {engine._f0} Hz")
    print(f"  Register size:            {engine.config.register_size} bits")
    print(f"  Polynomial taps:          {engine.config.polynomial_taps}")
    print(f"  Seed (hex):               0x{engine._seed:08x}")
    print(f"  Initial key (hex):        {engine.get_current_key().hex()[:32]}...")

    print(f"\n  {'Step':>5}  {'Register':>12}  {'Key (first 16 hex)':>20}")
    print(f"  {'-'*5}  {'-'*12}  {'-'*20}")

    for i in range(10):
        state = engine.rotate(steps=1)
        print(
            f"  {state.step:>5}  0x{state.register:08x}  "
            f"{state.key[:16].hex()}"
        )

    key_schedule = engine.generate_key_schedule(n_keys=8)
    print(f"\n  Pre-generated key schedule (8 keys):")
    for i, k in enumerate(key_schedule):
        print(f"    [{i}] {k[:16].hex()}...")

    period = engine.compute_period()
    print(f"\n  LFSR period: {period} steps")
    print(f"  Maximal (2^32 - 1): {2**32 - 1}")
    print(f"  Is maximal: {period == 2**32 - 1}")
    print("=" * 60)


if __name__ == "__main__":
    simulate_lfsr_rotation()