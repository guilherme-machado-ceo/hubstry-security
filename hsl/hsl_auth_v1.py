"""
HSL Auth v1 (PSK-HMAC) — experimental corrected HSL handshake
=============================================================

Status: experimental research protocol. Not reviewed, not validated, not
for production use. Supersedes the authentication logic of the historical
v0 simulation (``hsl/hsl_module.py``), which is kept unchanged as a record.

Security basis
--------------
Message authentication in v1 rests on a **pre-shared key (PSK)** of at
least 32 random bytes and on **HMAC-SHA-256** (RFC 2104 / FIPS 198-1).
The harmonic parameters (``f0``, ``base``) and each node's harmonic phase
slot are **protocol context and identification only**: they are bound into
the authenticated transcript, but they are not secrets and they do not
contribute to authentication strength.

Protocol (3 messages, directional MACs)
---------------------------------------
    1. Challenge  A -> B : id_A, slot_A, nonce_A, t_A
    2. Response   B -> A : id_B, slot_B, nonce_A, nonce_B,
                           tag_B = HMAC(K, "HSL-v1/response" || T)
    3. Verify     A -> B : nonce_B,
                           tag_A = HMAC(K, "HSL-v1/verify" || T || tag_B)

``T`` is a canonical, length-prefixed transcript of the protocol
identifier, f0, base and every field of messages 1 and 2. Distinct labels
per direction prevent a MAC produced in one direction from being accepted
in the other. Both sides derive the same ``session_id`` locally from
``HMAC(K, "HSL-v1/session" || T || tag_B)``; it is never transmitted.
The authentication result is local state and is never sent on the wire.

Assumptions and limitations (normative)
---------------------------------------
- The PSK is distributed out of band and is specific to the pair of nodes.
  Key distribution is out of scope.
- Replay detection is implemented for the lifetime of an engine instance,
  within the configured timestamp window. It does not survive a process
  restart and is not shared across instances.
- No forward secrecy: compromise of the PSK exposes the authenticity of
  past and future sessions under that key.
- No post-quantum signature is used. ML-DSA integration (audit finding
  F-01) depends on the PQC provider under review in PR #5.
- No claim is made about handshake size, performance, quantum resistance
  or equivalence with TLS 1.3.

Audit: docs/research/hsl-documentation-audit-2026-10.md (F-02 to F-09).

Author: Hubstry Deep Tech (guilhermemachado.ceo@hubstry.dev)
License: CC BY-NC-SA 4.0
"""

from __future__ import annotations

import hashlib
import hmac
import secrets
import struct
import time
from dataclasses import dataclass, field
from typing import Callable, Optional

PROTOCOL_ID = b"HSL-v1"
PROTOCOL_VERSION = 1

MSG_CHALLENGE = 1
MSG_RESPONSE = 2
MSG_VERIFY = 3

LABEL_RESPONSE = b"HSL-v1/response"
LABEL_VERIFY = b"HSL-v1/verify"
LABEL_SESSION = b"HSL-v1/session"

MIN_PSK_LEN = 32
NONCE_LEN = 32
TAG_LEN = 32
SESSION_ID_LEN = 16
MAX_ID_LEN = 255


class HSLAuthError(Exception):
    """Raised when a message is malformed or fails authentication checks."""


def generate_psk() -> bytes:
    """Return a fresh 32-byte random pre-shared key."""
    return secrets.token_bytes(MIN_PSK_LEN)


def harmonic_phase_slot(node_id: str, base: int) -> int:
    """
    Harmonic phase slot of a node: sha256(node_id) mod base.

    Same derivation as v0. Context and identification only: the slot is
    computable by anyone from the public node identifier.
    """
    digest = hashlib.sha256(node_id.encode("utf-8")).digest()
    return int.from_bytes(digest, "big") % base


# ---------------------------------------------------------------------------
# Canonical encoding helpers
# ---------------------------------------------------------------------------


def _lp(data: bytes) -> bytes:
    """Length-prefixed field for the transcript (u32 big-endian length)."""
    return struct.pack(">I", len(data)) + data


def _encode_id(node_id: str) -> bytes:
    raw = node_id.encode("utf-8")
    if not 1 <= len(raw) <= MAX_ID_LEN:
        raise HSLAuthError("node identifier must be 1..255 bytes in UTF-8")
    return raw


class _Reader:
    """Bounds-checked reader; rejects truncated input and trailing bytes."""

    def __init__(self, data: bytes) -> None:
        self._data = data
        self._pos = 0

    def take(self, n: int) -> bytes:
        if n < 0 or self._pos + n > len(self._data):
            raise HSLAuthError("truncated message")
        chunk = self._data[self._pos : self._pos + n]
        self._pos += n
        return chunk

    def u8(self) -> int:
        return self.take(1)[0]

    def u16(self) -> int:
        return struct.unpack(">H", self.take(2))[0]

    def u64(self) -> int:
        return struct.unpack(">Q", self.take(8))[0]

    def node_id(self) -> str:
        length = self.u8()
        if length == 0:
            raise HSLAuthError("empty node identifier")
        try:
            return self.take(length).decode("utf-8")
        except UnicodeDecodeError as exc:
            raise HSLAuthError("node identifier is not valid UTF-8") from exc

    def header(self, expected_type: int) -> None:
        if self.u8() != PROTOCOL_VERSION:
            raise HSLAuthError("unsupported protocol version")
        if self.u8() != expected_type:
            raise HSLAuthError("unexpected message type")

    def finish(self) -> None:
        if self._pos != len(self._data):
            raise HSLAuthError("trailing bytes after message")


def _header(msg_type: int) -> bytes:
    return bytes([PROTOCOL_VERSION, msg_type])


def _id_field(node_id: str) -> bytes:
    raw = _encode_id(node_id)
    return bytes([len(raw)]) + raw


def _check_len(name: str, value: bytes, expected: int) -> None:
    if len(value) != expected:
        raise HSLAuthError(f"{name} must be {expected} bytes")


# ---------------------------------------------------------------------------
# Messages
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Challenge:
    """Message 1 (A -> B)."""

    initiator_id: str
    phase_slot: int
    nonce_a: bytes
    timestamp: int

    def to_bytes(self) -> bytes:
        _check_len("nonce_a", self.nonce_a, NONCE_LEN)
        return (
            _header(MSG_CHALLENGE)
            + _id_field(self.initiator_id)
            + struct.pack(">H", self.phase_slot)
            + self.nonce_a
            + struct.pack(">Q", self.timestamp)
        )

    @classmethod
    def from_bytes(cls, data: bytes) -> "Challenge":
        r = _Reader(data)
        r.header(MSG_CHALLENGE)
        msg = cls(
            initiator_id=r.node_id(),
            phase_slot=r.u16(),
            nonce_a=r.take(NONCE_LEN),
            timestamp=r.u64(),
        )
        r.finish()
        return msg


@dataclass(frozen=True)
class Response:
    """Message 2 (B -> A)."""

    responder_id: str
    phase_slot: int
    nonce_a: bytes
    nonce_b: bytes
    tag_b: bytes

    def to_bytes(self) -> bytes:
        _check_len("nonce_a", self.nonce_a, NONCE_LEN)
        _check_len("nonce_b", self.nonce_b, NONCE_LEN)
        _check_len("tag_b", self.tag_b, TAG_LEN)
        return (
            _header(MSG_RESPONSE)
            + _id_field(self.responder_id)
            + struct.pack(">H", self.phase_slot)
            + self.nonce_a
            + self.nonce_b
            + self.tag_b
        )

    @classmethod
    def from_bytes(cls, data: bytes) -> "Response":
        r = _Reader(data)
        r.header(MSG_RESPONSE)
        msg = cls(
            responder_id=r.node_id(),
            phase_slot=r.u16(),
            nonce_a=r.take(NONCE_LEN),
            nonce_b=r.take(NONCE_LEN),
            tag_b=r.take(TAG_LEN),
        )
        r.finish()
        return msg


@dataclass(frozen=True)
class Verify:
    """Message 3 (A -> B). Carries no authentication flag."""

    nonce_b: bytes
    tag_a: bytes

    def to_bytes(self) -> bytes:
        _check_len("nonce_b", self.nonce_b, NONCE_LEN)
        _check_len("tag_a", self.tag_a, TAG_LEN)
        return _header(MSG_VERIFY) + self.nonce_b + self.tag_a

    @classmethod
    def from_bytes(cls, data: bytes) -> "Verify":
        r = _Reader(data)
        r.header(MSG_VERIFY)
        msg = cls(nonce_b=r.take(NONCE_LEN), tag_a=r.take(TAG_LEN))
        r.finish()
        return msg


@dataclass(frozen=True)
class Session:
    """Local result of a completed handshake. Never serialized."""

    peer_id: str
    role: str
    session_id: bytes = field(repr=False)

    def __repr__(self) -> str:
        return f"Session(peer_id={self.peer_id!r}, role={self.role!r})"


# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------


@dataclass
class HSLAuthConfig:
    """Protocol context. f0 and base are public parameters, not secrets."""

    f0: float = 440.0
    base: int = 12
    timestamp_window: int = 60


class HSLAuthEngine:
    """
    HSL Auth v1 engine for one node.

    Args:
        node_id: Public identifier of this node (1..255 bytes UTF-8).
        psk: Pre-shared key with the peer(s), at least 32 bytes.
        config: Public protocol context (f0, base, timestamp window).
        peers: Optional registry of allowed peer identifiers. When given,
            messages from identifiers outside the registry are rejected.
            This is a policy and consistency check, not authentication.
        clock: Time source in Unix seconds (injectable for tests).
    """

    def __init__(
        self,
        node_id: str,
        psk: bytes,
        config: Optional[HSLAuthConfig] = None,
        peers: Optional[set[str]] = None,
        clock: Callable[[], float] = time.time,
    ) -> None:
        _encode_id(node_id)
        if not isinstance(psk, (bytes, bytearray)) or len(psk) < MIN_PSK_LEN:
            raise HSLAuthError(f"psk must be at least {MIN_PSK_LEN} bytes")
        self.node_id = node_id
        self._psk = bytes(psk)
        self.config = config or HSLAuthConfig()
        self.peers = set(peers) if peers is not None else None
        self._clock = clock
        self._pending_initiator: dict[bytes, tuple[Challenge, str, float]] = {}
        self._pending_responder: dict[bytes, tuple[bytes, float, str]] = {}
        self._seen: dict[tuple[str, bytes], float] = {}

    def __repr__(self) -> str:
        return f"HSLAuthEngine(node_id={self.node_id!r}, config={self.config!r})"

    # -- helpers ------------------------------------------------------------

    @property
    def phase_slot(self) -> int:
        return harmonic_phase_slot(self.node_id, self.config.base)

    def _now(self) -> float:
        return float(self._clock())

    def _mac(self, label: bytes, data: bytes) -> bytes:
        return hmac.new(self._psk, label + data, hashlib.sha256).digest()

    def _transcript(self, challenge: Challenge, response_fields: tuple) -> bytes:
        responder_id, slot_b, nonce_b = response_fields
        return b"".join(
            [
                _lp(PROTOCOL_ID),
                _lp(struct.pack(">d", float(self.config.f0))),
                _lp(struct.pack(">H", self.config.base)),
                _lp(_encode_id(challenge.initiator_id)),
                _lp(struct.pack(">H", challenge.phase_slot)),
                _lp(challenge.nonce_a),
                _lp(struct.pack(">Q", challenge.timestamp)),
                _lp(_encode_id(responder_id)),
                _lp(struct.pack(">H", slot_b)),
                _lp(nonce_b),
            ]
        )

    def _check_peer(self, peer_id: str, slot: int) -> None:
        if peer_id == self.node_id:
            raise HSLAuthError("peer identifier equals own identifier")
        if self.peers is not None and peer_id not in self.peers:
            raise HSLAuthError("peer not in registry")
        if slot != harmonic_phase_slot(peer_id, self.config.base):
            raise HSLAuthError("phase slot inconsistent with peer identifier")

    def _expire(self) -> None:
        now = self._now()
        window = self.config.timestamp_window
        self._seen = {k: exp for k, exp in self._seen.items() if exp > now}
        self._pending_initiator = {
            k: v for k, v in self._pending_initiator.items() if now - v[2] <= window
        }
        self._pending_responder = {
            k: v for k, v in self._pending_responder.items() if now - v[1] <= window
        }

    # -- protocol -----------------------------------------------------------

    def initiate(self, peer_id: str) -> Challenge:
        """Step 1: create a challenge addressed to ``peer_id``."""
        _encode_id(peer_id)
        if peer_id == self.node_id:
            raise HSLAuthError("cannot initiate a handshake with itself")
        self._expire()
        challenge = Challenge(
            initiator_id=self.node_id,
            phase_slot=self.phase_slot,
            nonce_a=secrets.token_bytes(NONCE_LEN),
            timestamp=int(self._now()),
        )
        self._pending_initiator[challenge.nonce_a] = (challenge, peer_id, self._now())
        return challenge

    def respond(self, challenge: Challenge) -> Response:
        """Step 2: validate a challenge and return an authenticated response."""
        self._expire()
        _check_len("nonce_a", challenge.nonce_a, NONCE_LEN)
        self._check_peer(challenge.initiator_id, challenge.phase_slot)
        now = self._now()
        if abs(now - challenge.timestamp) > self.config.timestamp_window:
            raise HSLAuthError("challenge timestamp outside window")
        key = (challenge.initiator_id, challenge.nonce_a)
        if key in self._seen:
            raise HSLAuthError("replayed challenge")
        self._seen[key] = now + 2 * self.config.timestamp_window

        nonce_b = secrets.token_bytes(NONCE_LEN)
        transcript = self._transcript(challenge, (self.node_id, self.phase_slot, nonce_b))
        tag_b = self._mac(LABEL_RESPONSE, transcript)
        self._pending_responder[nonce_b] = (
            transcript + _lp(tag_b),
            now,
            challenge.initiator_id,
        )
        return Response(
            responder_id=self.node_id,
            phase_slot=self.phase_slot,
            nonce_a=challenge.nonce_a,
            nonce_b=nonce_b,
            tag_b=tag_b,
        )

    def finish(self, response: Response) -> tuple[Verify, Session]:
        """Step 3 (initiator): verify the response and produce the verify message."""
        self._expire()
        pending = self._pending_initiator.pop(response.nonce_a, None)
        if pending is None:
            raise HSLAuthError("no pending challenge for this response")
        challenge, expected_peer, _created = pending
        if response.responder_id != expected_peer:
            raise HSLAuthError("response from unexpected peer")
        self._check_peer(response.responder_id, response.phase_slot)
        _check_len("nonce_b", response.nonce_b, NONCE_LEN)

        transcript = self._transcript(
            challenge, (response.responder_id, response.phase_slot, response.nonce_b)
        )
        expected_tag_b = self._mac(LABEL_RESPONSE, transcript)
        if not hmac.compare_digest(expected_tag_b, response.tag_b):
            raise HSLAuthError("response authentication failed")

        bound = transcript + _lp(response.tag_b)
        tag_a = self._mac(LABEL_VERIFY, bound)
        session_id = self._mac(LABEL_SESSION, bound)[:SESSION_ID_LEN]
        return (
            Verify(nonce_b=response.nonce_b, tag_a=tag_a),
            Session(peer_id=response.responder_id, role="initiator", session_id=session_id),
        )

    def complete(self, verify: Verify) -> Session:
        """Step 3 (responder): verify the initiator's final message."""
        self._expire()
        pending = self._pending_responder.pop(verify.nonce_b, None)
        if pending is None:
            raise HSLAuthError("no pending session for this verify message")
        bound, _created, initiator_id = pending
        expected_tag_a = self._mac(LABEL_VERIFY, bound)
        if not hmac.compare_digest(expected_tag_a, verify.tag_a):
            raise HSLAuthError("verify authentication failed")
        session_id = self._mac(LABEL_SESSION, bound)[:SESSION_ID_LEN]
        return Session(peer_id=initiator_id, role="responder", session_id=session_id)


def simulate_protocol() -> None:
    """Run one handshake between two nodes and print the measured sizes."""
    psk = generate_psk()
    alice = HSLAuthEngine("alice-node-01", psk)
    bob = HSLAuthEngine("bob-node-02", psk)

    challenge = alice.initiate("bob-node-02")
    response = bob.respond(Challenge.from_bytes(challenge.to_bytes()))
    verify, alice_session = alice.finish(Response.from_bytes(response.to_bytes()))
    bob_session = bob.complete(Verify.from_bytes(verify.to_bytes()))

    sizes = [len(m.to_bytes()) for m in (challenge, response, verify)]
    print("HSL Auth v1 (PSK-HMAC) — experimental")
    print(f"  message sizes (bytes): {sizes}  total: {sum(sizes)}")
    print(f"  initiator: {alice_session}")
    print(f"  responder: {bob_session}")
    print(f"  session ids match: {alice_session.session_id == bob_session.session_id}")


if __name__ == "__main__":
    simulate_protocol()
