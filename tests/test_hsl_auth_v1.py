"""
tests/test_hsl_auth_v1.py — tests for hsl/hsl_auth_v1.py (HSL Auth v1, PSK-HMAC).

Covers the corrections for audit findings F-02 to F-09: keyed MAC,
secret-based acceptance (F-03 regression), peer consistency checks,
verification of step 3, canonical framing, no authentication flag on the
wire, replay detection and reflection resistance. Sizes are measured and
recorded, not compared with any historical target.

Run from repository root:  pytest tests/ -v
"""

from __future__ import annotations

import dataclasses
import hashlib
import hmac
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from hsl.hsl_auth_v1 import (  # noqa: E402
    LABEL_RESPONSE,
    LABEL_VERIFY,
    Challenge,
    HSLAuthConfig,
    HSLAuthEngine,
    HSLAuthError,
    Response,
    Verify,
    generate_psk,
    harmonic_phase_slot,
)

A, B = "alice-node-01", "bob-node-02"


class Clock:
    def __init__(self, t: float = 1_800_000_000.0) -> None:
        self.t = t

    def __call__(self) -> float:
        return self.t


def wire(msg):
    """Round-trip a message through its byte encoding."""
    return type(msg).from_bytes(msg.to_bytes())


def pair(psk=None, clock=None, **kw):
    psk = psk or generate_psk()
    clock = clock or Clock()
    return (
        HSLAuthEngine(A, psk, clock=clock, **kw),
        HSLAuthEngine(B, psk, clock=clock, **kw),
    )


def full_handshake(alice, bob):
    challenge = alice.initiate(B)
    response = bob.respond(wire(challenge))
    verify, s_alice = alice.finish(wire(response))
    s_bob = bob.complete(wire(verify))
    return challenge, response, verify, s_alice, s_bob


# --- correct operation --------------------------------------------------------


def test_honest_handshake_succeeds_and_sessions_match():
    alice, bob = pair()
    _, _, _, s_alice, s_bob = full_handshake(alice, bob)
    assert s_alice.peer_id == B and s_bob.peer_id == A
    assert s_alice.session_id == s_bob.session_id
    assert len(s_alice.session_id) == 16


def test_sessions_are_unique_per_handshake():
    alice, bob = pair()
    first = full_handshake(alice, bob)[3].session_id
    second = full_handshake(alice, bob)[3].session_id
    assert first != second


# --- F-03 regression: acceptance requires the secret ------------------------------


def test_f03_attacker_knowing_f0_but_not_key_is_rejected():
    clock = Clock()
    psk = generate_psk()
    alice = HSLAuthEngine(A, psk, clock=clock)
    mallory = HSLAuthEngine(B, generate_psk(), clock=clock)  # same id, f0, base
    response = mallory.respond(wire(alice.initiate(B)))
    with pytest.raises(HSLAuthError, match="response authentication failed"):
        alice.finish(wire(response))


def test_f03_attacker_cannot_complete_as_initiator_without_key():
    clock = Clock()
    psk = generate_psk()
    bob = HSLAuthEngine(B, psk, clock=clock)
    mallory = HSLAuthEngine(A, generate_psk(), clock=clock)
    response = bob.respond(wire(mallory.initiate(B)))
    forged = Verify(nonce_b=response.nonce_b, tag_a=b"\x00" * 32)
    with pytest.raises(HSLAuthError, match="verify authentication failed"):
        bob.complete(wire(forged))


def test_wrong_context_f0_is_rejected():
    clock = Clock()
    psk = generate_psk()
    alice = HSLAuthEngine(A, psk, clock=clock)
    bob = HSLAuthEngine(B, psk, config=HSLAuthConfig(f0=441.0), clock=clock)
    response = bob.respond(wire(alice.initiate(B)))
    with pytest.raises(HSLAuthError):
        alice.finish(wire(response))


# --- F-02: keyed MAC ---------------------------------------------------------------


def test_f02_response_tag_is_hmac_over_transcript():
    alice, bob = pair()
    challenge = alice.initiate(B)
    response = bob.respond(wire(challenge))
    transcript = bob._transcript(challenge, (B, response.phase_slot, response.nonce_b))
    expected = hmac.new(bob._psk, LABEL_RESPONSE + transcript, hashlib.sha256).digest()
    assert response.tag_b == expected
    unkeyed = hashlib.sha256(LABEL_RESPONSE + transcript).digest()
    assert response.tag_b != unkeyed


# --- tampering ---------------------------------------------------------------------


@pytest.mark.parametrize("field_name", ["phase_slot", "nonce_b", "tag_b"])
def test_tampered_response_is_rejected(field_name):
    alice, bob = pair()
    response = bob.respond(wire(alice.initiate(B)))
    value = getattr(response, field_name)
    if isinstance(value, int):
        tampered = (value + 1) % 12
    else:
        tampered = bytes([value[0] ^ 1]) + value[1:]
    bad = dataclasses.replace(response, **{field_name: tampered})
    with pytest.raises(HSLAuthError):
        alice.finish(wire(bad))


@pytest.mark.parametrize("field_name", ["nonce_a", "timestamp"])
def test_tampered_challenge_breaks_authentication(field_name):
    alice, bob = pair()
    challenge = alice.initiate(B)
    value = getattr(challenge, field_name)
    tampered = value - 1 if isinstance(value, int) else bytes([value[0] ^ 1]) + value[1:]
    bad = dataclasses.replace(challenge, **{field_name: tampered})
    response = bob.respond(wire(bad))
    with pytest.raises(HSLAuthError):
        alice.finish(wire(response))


def test_f05_tampered_verify_is_rejected():
    alice, bob = pair()
    response = bob.respond(wire(alice.initiate(B)))
    verify, _ = alice.finish(wire(response))
    bad = Verify(nonce_b=verify.nonce_b, tag_a=bytes([verify.tag_a[0] ^ 1]) + verify.tag_a[1:])
    with pytest.raises(HSLAuthError, match="verify authentication failed"):
        bob.complete(wire(bad))


# --- F-04: peer consistency (context, not authentication) -------------------------


def test_f04_inconsistent_phase_slot_is_rejected():
    alice, bob = pair()
    challenge = alice.initiate(B)
    wrong = (harmonic_phase_slot(A, 12) + 1) % 12
    with pytest.raises(HSLAuthError, match="phase slot"):
        bob.respond(wire(dataclasses.replace(challenge, phase_slot=wrong)))


def test_f04_peer_registry_is_enforced():
    psk, clock = generate_psk(), Clock()
    alice = HSLAuthEngine(A, psk, clock=clock)
    bob = HSLAuthEngine(B, psk, clock=clock, peers={"someone-else"})
    with pytest.raises(HSLAuthError, match="registry"):
        bob.respond(wire(alice.initiate(B)))


# --- F-08: replay -----------------------------------------------------------------


def test_f08_replayed_challenge_is_rejected():
    alice, bob = pair()
    challenge = wire(alice.initiate(B))
    bob.respond(challenge)
    with pytest.raises(HSLAuthError, match="replayed"):
        bob.respond(challenge)


def test_f08_replayed_verify_is_rejected():
    alice, bob = pair()
    _, _, verify, _, _ = full_handshake(alice, bob)
    with pytest.raises(HSLAuthError, match="no pending session"):
        bob.complete(wire(verify))


def test_replayed_response_is_rejected():
    alice, bob = pair()
    response = bob.respond(wire(alice.initiate(B)))
    alice.finish(wire(response))
    with pytest.raises(HSLAuthError, match="no pending challenge"):
        alice.finish(wire(response))


def test_stale_challenge_is_rejected():
    clock = Clock()
    alice, bob = pair(clock=clock)
    challenge = alice.initiate(B)
    clock.t += 61
    with pytest.raises(HSLAuthError, match="outside window"):
        bob.respond(wire(challenge))


def test_expired_pending_challenge_is_rejected():
    clock = Clock()
    alice, bob = pair(clock=clock)
    response = bob.respond(wire(alice.initiate(B)))
    clock.t += 61
    with pytest.raises(HSLAuthError, match="no pending challenge"):
        alice.finish(wire(response))


# --- reflection and direction separation ------------------------------------------


def test_reflection_of_own_challenge_is_rejected():
    clock, psk = Clock(), generate_psk()
    alice = HSLAuthEngine(A, psk, clock=clock)
    with pytest.raises(HSLAuthError, match="own identifier"):
        alice.respond(wire(alice.initiate(B)))


def test_response_from_unexpected_peer_is_rejected():
    clock, psk = Clock(), generate_psk()
    alice = HSLAuthEngine(A, psk, clock=clock)
    carol = HSLAuthEngine("carol-node-03", psk, clock=clock)
    response = carol.respond(wire(alice.initiate(B)))
    with pytest.raises(HSLAuthError, match="unexpected peer"):
        alice.finish(wire(response))


def test_response_tag_cannot_be_used_as_verify_tag():
    alice, bob = pair()
    response = bob.respond(wire(alice.initiate(B)))
    alice.finish(wire(response))
    misused = Verify(nonce_b=response.nonce_b, tag_a=response.tag_b)
    with pytest.raises(HSLAuthError):
        bob.complete(wire(misused))


def test_directional_labels_are_distinct():
    assert LABEL_RESPONSE != LABEL_VERIFY


# --- F-06 / F-07: framing and wire content ----------------------------------------


def test_f06_roundtrip_preserves_all_fields():
    alice, bob = pair()
    challenge = alice.initiate(B)
    response = bob.respond(wire(challenge))
    verify, _ = alice.finish(wire(response))
    for msg in (challenge, response, verify):
        assert wire(msg) == msg


@pytest.mark.parametrize("cls", [Challenge, Response, Verify])
def test_f06_truncated_and_trailing_bytes_are_rejected(cls):
    alice, bob = pair()
    challenge = alice.initiate(B)
    response = bob.respond(wire(challenge))
    verify, _ = alice.finish(wire(response))
    raw = {Challenge: challenge, Response: response, Verify: verify}[cls].to_bytes()
    with pytest.raises(HSLAuthError):
        cls.from_bytes(raw[:-1])
    with pytest.raises(HSLAuthError):
        cls.from_bytes(raw + b"\x00")


def test_f06_wrong_message_type_is_rejected():
    alice, _ = pair()
    with pytest.raises(HSLAuthError, match="message type"):
        Response.from_bytes(alice.initiate(B).to_bytes())


def test_f07_no_authentication_flag_on_the_wire():
    for cls in (Challenge, Response, Verify):
        names = {f.name for f in dataclasses.fields(cls)}
        assert "authenticated" not in names


# --- configuration and secrecy hygiene --------------------------------------------


def test_short_psk_is_rejected():
    with pytest.raises(HSLAuthError, match="psk"):
        HSLAuthEngine(A, b"\x01" * 31)


def test_repr_does_not_expose_secrets():
    psk = generate_psk()
    alice, bob = pair(psk=psk)
    _, _, _, s_alice, _ = full_handshake(alice, bob)
    for text in (repr(alice), repr(s_alice)):
        assert psk.hex() not in text
        assert s_alice.session_id.hex() not in text


# --- measurement (recorded, not compared with any target) -------------------------


def test_measured_sizes_are_recorded(capsys):
    alice, bob = pair()
    challenge, response, verify, _, _ = full_handshake(alice, bob)
    sizes = [len(m.to_bytes()) for m in (challenge, response, verify)]
    id_a, id_b = len(A.encode()), len(B.encode())
    assert sizes == [2 + 1 + id_a + 2 + 32 + 8, 2 + 1 + id_b + 2 + 32 + 32 + 32, 2 + 32 + 32]
    print(f"HSL v1 measured sizes (ids {id_a}/{id_b} B): {sizes} total {sum(sizes)}")


# --- H-1: invalid messages must not consume pending state ----------------------


@pytest.mark.parametrize(
    "field_name,value",
    [
        ("tag_b", b"\x00" * 32),
        ("responder_id", "mallory-node-99"),
        ("phase_slot", (harmonic_phase_slot(B, 12) + 1) % 12),
        ("nonce_b", b"\x01" * 31),
    ],
)
def test_h1_invalid_response_does_not_cancel_handshake(field_name, value):
    alice, bob = pair()
    challenge = alice.initiate(B)
    response = bob.respond(wire(challenge))
    forged = dataclasses.replace(response, **{field_name: value})
    with pytest.raises(HSLAuthError):
        alice.finish(forged)  # not serialized: also covers fields the wire format would reject
    verify, s_alice = alice.finish(wire(response))
    s_bob = bob.complete(wire(verify))
    assert s_alice.session_id == s_bob.session_id


def test_h1_invalid_verify_does_not_cancel_handshake():
    alice, bob = pair()
    response = bob.respond(wire(alice.initiate(B)))
    verify, s_alice = alice.finish(wire(response))
    forged = Verify(nonce_b=verify.nonce_b, tag_a=b"\x00" * 32)
    with pytest.raises(HSLAuthError, match="verify authentication failed"):
        bob.complete(wire(forged))
    assert bob.complete(wire(verify)).session_id == s_alice.session_id


def test_h1_state_is_consumed_after_success():
    alice, bob = pair()
    _, response, verify, _, _ = full_handshake(alice, bob)
    with pytest.raises(HSLAuthError, match="no pending challenge"):
        alice.finish(wire(response))
    with pytest.raises(HSLAuthError, match="no pending session"):
        bob.complete(wire(verify))


# --- H-5: replay protection covers the whole acceptance window -----------------


def test_h5_replay_rejected_at_window_boundary():
    psk = generate_psk()
    alice_clock, bob_clock = Clock(1_800_000_060.0), Clock(1_800_000_000.0)
    alice = HSLAuthEngine(A, psk, clock=alice_clock)
    bob = HSLAuthEngine(B, psk, clock=bob_clock)
    challenge = wire(alice.initiate(B))  # timestamp W ahead of bob's clock
    bob.respond(challenge)
    bob_clock.t = challenge.timestamp + 60  # last instant the timestamp is accepted
    with pytest.raises(HSLAuthError, match="replayed"):
        bob.respond(challenge)


def test_h5_challenge_rejected_after_window_even_without_registry():
    alice, bob = pair()
    challenge = wire(alice.initiate(B))
    bob.respond(challenge)
    bob._clock.t += 61
    with pytest.raises(HSLAuthError, match="outside window"):
        bob.respond(challenge)


# --- H-6: configuration validation ----------------------------------------------


@pytest.mark.parametrize(
    "kwargs",
    [
        {"base": 0},
        {"base": 65536},
        {"base": -1},
        {"base": 12.0},
        {"f0": float("nan")},
        {"f0": float("inf")},
        {"f0": 0.0},
        {"f0": -0.0},
        {"f0": -440.0},
        {"f0": 10**400},
        {"f0": "440"},
        {"f0": True},
        {"base": True},
        {"timestamp_window": 0},
        {"timestamp_window": -1},
        {"timestamp_window": float("nan")},
        {"timestamp_window": "60"},
    ],
)
def test_h6_invalid_configuration_is_rejected(kwargs):
    with pytest.raises(HSLAuthError):
        HSLAuthConfig(**kwargs)


def test_h6_valid_boundary_configuration_is_accepted():
    alice, bob = pair(config=HSLAuthConfig(f0=1e-9, base=65535, timestamp_window=1))
    full_handshake(alice, bob)


def test_h6_configuration_is_immutable():
    config = HSLAuthConfig()
    with pytest.raises(dataclasses.FrozenInstanceError):
        config.base = 0  # type: ignore[misc]


def test_h6_float_window_and_numeric_f0_types_are_accepted():
    alice, bob = pair(config=HSLAuthConfig(f0=440, timestamp_window=60.0))
    full_handshake(alice, bob)


def test_peer_registry_is_immutable():
    psk = generate_psk()
    bob = HSLAuthEngine(B, psk, peers={A})
    with pytest.raises(AttributeError):
        bob.peers.add("mallory")  # type: ignore[union-attr]


# --- concurrency: the internal lock serializes state transitions ---------------


def test_concurrent_finish_completes_exactly_once():
    import threading

    for _ in range(50):
        alice, bob = pair()
        response = wire(bob.respond(wire(alice.initiate(B))))
        barrier = threading.Barrier(8)
        outcomes: list = []

        def worker():
            barrier.wait()
            try:
                alice.finish(response)
                outcomes.append("ok")
            except HSLAuthError:
                outcomes.append("rejected")

        threads = [threading.Thread(target=worker) for _ in range(8)]
        for th in threads:
            th.start()
        for th in threads:
            th.join()
        assert outcomes.count("ok") == 1
        assert outcomes.count("rejected") == 7
