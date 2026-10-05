"""
tests/test_hsl_v0_regression.py — reproducible record of audit findings
against the historical HSL v0 simulation (``hsl/hsl_module.py``).

These tests PASS when the known weakness is reproduced. They document the
behaviour of v0 and must not be read as properties of HSL. The corrected
protocol is ``hsl/hsl_auth_v1.py`` (see tests/test_hsl_auth_v1.py).

Audit: docs/research/hsl-documentation-audit-2026-10.md

Run from repository root:  pytest tests/ -v
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from hsl.hsl_module import HSLEngine, HSLEngineConfig  # noqa: E402


def _handshake(initiator: HSLEngine, responder: HSLEngine):
    challenge = initiator.create_challenge()
    response = responder.process_challenge(challenge)
    return challenge, response, initiator.verify_response(challenge, response)


def test_v0_f03_reproduces_acceptance_without_secret():
    """F-03: an unregistered node with the documented default f0 is accepted."""
    alice = HSLEngine("alice-node-01")
    mallory = HSLEngine("mallory")  # never registered anywhere
    _, _, verify = _handshake(alice, mallory)
    assert verify.authenticated is True


def test_v0_f03_acceptance_depends_only_on_f0():
    """F-03: changing f0 alone flips the outcome; no other secret is involved."""
    alice = HSLEngine("alice-node-01")
    mallory = HSLEngine("mallory", HSLEngineConfig(f0=441.0))
    _, _, verify = _handshake(alice, mallory)
    assert verify.authenticated is False


def test_v0_f01_signature_is_hash_placeholder():
    """F-01: the step-3 'signature' equals SHA-512(token || str(f0)) truncated."""
    alice = HSLEngine("alice-node-01")
    bob = HSLEngine("bob-node-02")
    _, _, verify = _handshake(alice, bob)
    expected = hashlib.sha512(
        verify.token_ab + str(alice.config.f0).encode("utf-8")
    ).digest()[:64]
    assert verify.sign_a == expected


def test_v0_f02_coherence_signature_is_unkeyed_sha256():
    """F-02: sigma is plain SHA-256 over public fields and f0 (no HMAC key)."""
    alice = HSLEngine("alice-node-01")
    bob = HSLEngine("bob-node-02")
    challenge, response, _ = _handshake(alice, bob)
    material = (
        challenge.phase_a.encode()
        + response.phase_b.encode()
        + challenge.nonce_a
        + response.nonce_b
        + str(bob.config.f0).encode("utf-8")
    )
    assert response.sigma_a_b == hashlib.sha256(material).digest()


def test_v0_reference_run_serialized_size():
    """Records the serialized size of the v0 reference run (audit: 249 B)."""
    alice = HSLEngine("alice-node-01")
    bob = HSLEngine("bob-node-02")
    challenge, response, verify = _handshake(alice, bob)
    sizes = (
        len(challenge.to_bytes()),
        len(response.to_bytes()),
        len(verify.to_bytes()),
    )
    assert sizes == (57, 79, 113)
    assert sum(sizes) == 249
