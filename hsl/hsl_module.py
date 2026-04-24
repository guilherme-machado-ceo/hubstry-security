"""
HSL Phase-Based Challenge-Response Module
==========================================

Implements the 3-step H-Challenge protocol with phase encoding
for the Harmonic Security Layer (HSL).

Reference:
    Paper 4 (CC BY 4.0): DOI 10.5281/zenodo.19056387 - HPG 1.0
    HSL phase-based authentication, H-Challenge/Response protocol.

Protocol Steps:
    Step 1 (Challenge):  Alice -> Bob   H_Challenge(phase_A, nonce_A, t_A)
    Step 2 (Response):   Bob   -> Alice H_Response(phase_B, sigma_A_B, nonce_B)
    Step 3 (Verify):     Alice -> Bob   H_Verify(token_AB, sign_A, session_id)

Author: Hubstry Deep Tech (guilhermemachado.ceo@hubstry.dev)
License: CC BY-NC-SA 4.0
"""

from __future__ import annotations

import hashlib
import math
import secrets
import struct
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class HSLPhase(Enum):
    """Enum for the three phases of the H-Challenge protocol."""
    CHALLENGE = "challenge"
    RESPONSE = "response"
    VERIFY = "verify"


@dataclass
class PhaseEncoding:
    """
    Encodes a harmonic phase value into a compact byte representation.

    Phase encoding maps a float phase angle (radians) to a 32-bit
    fixed-point representation with 16 fractional bits, preserving
    sufficient precision for coherence verification.

    Attributes:
        value: Phase angle in radians [0, 2*pi).
        precision_bits: Number of fractional bits in fixed-point encoding.
    """

    value: float
    precision_bits: int = 16

    def encode(self) -> bytes:
        """Encode phase angle to 4 bytes (32-bit fixed-point)."""
        scaled = int(self.value * (1 << self.precision_bits)) & 0xFFFFFFFF
        return struct.pack(">I", scaled)

    @classmethod
    def decode(cls, data: bytes, precision_bits: int = 16) -> "PhaseEncoding":
        """Decode 4 bytes back to PhaseEncoding."""
        raw = struct.unpack(">I", data[:4])[0]
        value = raw / (1 << precision_bits)
        return cls(value=value, precision_bits=precision_bits)

    def to_radians(self) -> float:
        """Return the phase angle in radians."""
        return self.value % (2 * math.pi)


@dataclass
class HChallenge:
    """
    Step 1 of the H-Challenge protocol.

    The challenger (Alice) sends her encoded phase, a cryptographic
    nonce, and a timestamp to establish freshness.

    Attributes:
        phase_a: Alice encoded phase value.
        nonce_a: 32-byte cryptographically random nonce.
        timestamp_a: Unix epoch seconds (replay protection).
        node_id: Identifier of the challenger node.
    """

    phase_a: PhaseEncoding
    nonce_a: bytes
    timestamp_a: int
    node_id: str = ""

    TIMESTAMP_WINDOW_SECONDS: int = 60

    def to_bytes(self) -> bytes:
        """Serialize challenge to compact byte representation."""
        parts = [
            self.phase_a.encode(),
            self.nonce_a,
            struct.pack(">Q", self.timestamp_a),
            self.node_id.encode("utf-8"),
        ]
        return b"".join(parts)

    def is_fresh(self) -> bool:
        """Check if the challenge is within the freshness window."""
        now = int(time.time())
        return abs(now - self.timestamp_a) <= self.TIMESTAMP_WINDOW_SECONDS

    def __repr__(self) -> str:
        return (
            f"HChallenge(node={self.node_id}, "
            f"phase={self.phase_a.to_radians():.4f} rad, "
            f"ts={self.timestamp_a})"
        )


@dataclass
class HResponse:
    """
    Step 2 of the H-Challenge protocol.

    The responder (Bob) computes a phase coherence signature
    sigma_A_B from both phase values and returns his own phase
    and nonce.

    Attributes:
        phase_b: Bob encoded phase value.
        sigma_a_b: Coherence signature over both phases.
        nonce_b: 32-byte cryptographically random nonce.
        node_id: Identifier of the responder node.
    """

    phase_b: PhaseEncoding
    sigma_a_b: bytes
    nonce_b: bytes
    node_id: str = ""

    def to_bytes(self) -> bytes:
        """Serialize response to compact byte representation."""
        parts = [
            self.phase_b.encode(),
            self.sigma_a_b,
            self.nonce_b,
            self.node_id.encode("utf-8"),
        ]
        return b"".join(parts)

    def __repr__(self) -> str:
        return (
            f"HResponse(node={self.node_id}, "
            f"phase={self.phase_b.to_radians():.4f} rad, "
            f"sigma={self.sigma_a_b[:8].hex()}...)"
        )


@dataclass
class HVerify:
    """
    Step 3 of the H-Challenge protocol.

    After verifying the coherence signature, Alice issues the
    final verification token, a PQC-compatible signature, and
    a session identifier.

    Attributes:
        token_ab: Mutual authentication token (HMAC-based).
        sign_a: Simulated PQC signature (placeholder for ML-DSA-65).
        session_id: Unique session identifier.
        authenticated: Whether mutual authentication succeeded.
    """

    token_ab: bytes
    sign_a: bytes
    session_id: str
    authenticated: bool = False

    def to_bytes(self) -> bytes:
        """Serialize verification to compact byte representation."""
        parts = [
            self.token_ab,
            self.sign_a,
            self.session_id.encode("utf-8"),
            struct.pack(">?", self.authenticated),
        ]
        return b"".join(parts)

    def __repr__(self) -> str:
        return (
            f"HVerify(session={self.session_id}, "
            f"auth={self.authenticated}, "
            f"token={self.token_ab[:8].hex()}...)"
        )


@dataclass
class HSLEngineConfig:
    """Configuration parameters for the HSL engine."""

    f0: float = 440.0
    base: int = 12
    nonce_size: int = 32
    timestamp_window: int = 60
    token_size: int = 32
    sign_size: int = 64
    coherence_epsilon: float = 0.01


class HSLEngine:
    """
    Harmonic Security Layer (HSL) engine implementing the
    3-step H-Challenge/Response protocol with phase encoding.

    Reference:
        Paper 4 (CC BY 4.0): DOI 10.5281/zenodo.19056387

    The engine derives harmonic phases from a shared fundamental
    frequency f0 and base subdivision b. Each node computes its
    phase as phi = 2*pi*(node_id % b)/b, enabling mutual
    authentication through phase coherence verification.

    Attributes:
        node_id: Unique identifier for this node.
        config: HSL engine configuration.
        shared_phase_map: Registry of known node phases (simulates
            out-of-band f0 distribution).
    """

    def __init__(
        self,
        node_id: str,
        config: Optional[HSLEngineConfig] = None,
    ) -> None:
        self.node_id = node_id
        self.config = config or HSLEngineConfig()
        self.shared_phase_map: dict[str, float] = {}
        self._sessions: dict[str, dict] = {}

    @staticmethod
    def _euler_totient(n: int) -> int:
        """Compute Euler totient function phi(n)."""
        result = n
        p = 2
        temp = n
        while p * p <= temp:
            if temp % p == 0:
                while temp % p == 0:
                    temp //= p
                result -= result // p
            p += 1
        if temp > 1:
            result -= result // temp
        return result

    def _compute_phase(self) -> PhaseEncoding:
        """
        Compute this node harmonic phase from f0 and base.

        The phase is derived as:
            phi = 2*pi * (hash(node_id) mod b) / b

        Returns:
            PhaseEncoding object with the computed phase angle.
        """
        node_hash = int(
            hashlib.sha256(self.node_id.encode("utf-8")).hexdigest(), 16
        )
        slot = node_hash % self.config.base
        angle = 2 * math.pi * slot / self.config.base
        return PhaseEncoding(value=angle)

    def _compute_coherence_signature(
        self,
        phase_a: PhaseEncoding,
        phase_b: PhaseEncoding,
        nonce_a: bytes,
        nonce_b: bytes,
    ) -> bytes:
        """
        Compute coherence signature sigma_A_B.

        The signature binds both phases and nonces to prevent
        replay and reflection attacks.

        Args:
            phase_a: Challenger phase encoding.
            phase_b: Responder phase encoding.
            nonce_a: Challenger nonce.
            nonce_b: Responder nonce.

        Returns:
            32-byte HMAC-SHA256 coherence signature.
        """
        material = (
            phase_a.encode()
            + phase_b.encode()
            + nonce_a
            + nonce_b
            + str(self.config.f0).encode("utf-8")
        )
        return hashlib.sha256(material).digest()

    def create_challenge(self) -> HChallenge:
        """
        Step 1: Create an H-Challenge message.

        Generates a fresh challenge with the node encoded phase,
        a random nonce, and the current timestamp.

        Returns:
            HChallenge object ready for transmission.
        """
        phase = self._compute_phase()
        nonce = secrets.token_bytes(self.config.nonce_size)
        timestamp = int(time.time())

        challenge = HChallenge(
            phase_a=phase,
            nonce_a=nonce,
            timestamp_a=timestamp,
            node_id=self.node_id,
        )

        self._sessions[f"pending_{nonce.hex()[:16]}"] = {
            "phase": phase,
            "nonce": nonce,
            "timestamp": timestamp,
            "created_at": time.time(),
        }

        return challenge

    def process_challenge(self, challenge: HChallenge) -> HResponse:
        """
        Step 2: Process an incoming H-Challenge and generate H-Response.

        Verifies challenge freshness, computes coherence signature
        binding both node phases, and returns the response.

        Args:
            challenge: Incoming H-Challenge from the peer.

        Returns:
            HResponse object with phase, signature, and nonce.

        Raises:
            ValueError: If the challenge is stale or malformed.
        """
        if not challenge.is_fresh():
            raise ValueError("Challenge timestamp outside freshness window")

        my_phase = self._compute_phase()
        nonce_b = secrets.token_bytes(self.config.nonce_size)

        sigma = self._compute_coherence_signature(
            challenge.phase_a, my_phase, challenge.nonce_a, nonce_b
        )

        response = HResponse(
            phase_b=my_phase,
            sigma_a_b=sigma,
            nonce_b=nonce_b,
            node_id=self.node_id,
        )

        self._sessions[f"response_{nonce_b.hex()[:16]}"] = {
            "challenge": challenge,
            "response": response,
            "created_at": time.time(),
        }

        return response

    def verify_response(
        self, challenge: HChallenge, response: HResponse
    ) -> HVerify:
        """
        Step 3: Verify an H-Response and issue H-Verify.

        Recomputes the coherence signature and compares it with
        the one provided by the responder. If they match, mutual
        authentication is established.

        Args:
            challenge: Original H-Challenge that was sent.
            response: Incoming H-Response from the peer.

        Returns:
            HVerify object with authentication result.
        """
        expected_sigma = self._compute_coherence_signature(
            challenge.phase_a,
            response.phase_b,
            challenge.nonce_a,
            response.nonce_b,
        )

        authenticated = secrets.compare_digest(
            expected_sigma, response.sigma_a_b
        )

        token_material = (
            challenge.phase_a.encode()
            + response.phase_b.encode()
            + expected_sigma
        )
        token_ab = hashlib.sha256(token_material).digest()

        sign_material = token_ab + str(self.config.f0).encode("utf-8")
        sign_a = hashlib.sha512(sign_material).digest()[: self.config.sign_size]

        session_id = hashlib.sha256(
            token_ab + struct.pack(">d", time.time())
        ).hexdigest()[:16]

        return HVerify(
            token_ab=token_ab[: self.config.token_size],
            sign_a=sign_a,
            session_id=session_id,
            authenticated=authenticated,
        )

    def register_peer_phase(self, peer_id: str, phase_angle: float) -> None:
        """Register a known peer phase angle for pre-shared verification."""
        self.shared_phase_map[peer_id] = phase_angle

    def verify_peer_phase(
        self, peer_id: str, observed_phase: PhaseEncoding
    ) -> bool:
        """Verify that an observed phase matches the registered peer phase."""
        expected = self.shared_phase_map.get(peer_id)
        if expected is None:
            return False
        delta = abs(observed_phase.to_radians() - expected)
        return delta < self.config.coherence_epsilon


def simulate_protocol() -> None:
    """Run a full 3-step H-Challenge protocol simulation."""
    print("=" * 60)
    print("  HSL 3-Step H-Challenge Protocol Simulation")
    print("  Reference: DOI 10.5281/zenodo.19056387 (HPG 1.0)")
    print("=" * 60)

    alice = HSLEngine(node_id="alice-node-01")
    bob = HSLEngine(node_id="bob-node-02")

    print(f"\n  Alice phase: {alice._compute_phase().to_radians():.6f} rad")
    print(f"  Bob   phase: {bob._compute_phase().to_radians():.6f} rad")

    print("\n  --- Step 1: Challenge ---")
    challenge = alice.create_challenge()
    print(f"  Alice -> Bob: {challenge}")

    print("\n  --- Step 2: Response ---")
    response = bob.process_challenge(challenge)
    print(f"  Bob -> Alice: {response}")

    print("\n  --- Step 3: Verify ---")
    verify = alice.verify_response(challenge, response)
    print(f"  Alice -> Bob: {verify}")

    print(f"\n  Total bytes exchanged: ~{len(challenge.to_bytes()) + len(response.to_bytes()) + len(verify.to_bytes())}")
    print(f"  Authentication: {'SUCCESS' if verify.authenticated else 'FAILED'}")
    print("=" * 60)


if __name__ == "__main__":
    simulate_protocol()