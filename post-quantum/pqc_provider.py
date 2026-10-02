"""
PQCProvider — crypto-agile post-quantum provider (PR2, spec v1.2)
==================================================================

Application-level facade over the liboqs backend (gate G1). Implements:

- ALGORITHM_REGISTRY with active / watchlist(blocked) status;
  FN-DSA and HQC are hard-blocked for this cycle (spec v1.2, section 10);
- ML-KEM-768 (FIPS 203) key establishment [STANDARDIZED]
- ML-DSA-65 (FIPS 204) and SLH-DSA-SHA2-128s (FIPS 205) signatures
  [STANDARDIZED]
- HKDF-SHA-256 key schedule (RFC 5869) with NORMATIVE length-prefixed
  ``info`` encoding (spec v1.2, section 6.1 — composition frozen)
- Canonical, versioned, domain-separated transcript serialization
  (spec v1.2, gate G3)

PR2 scope (review-driven, 2026-10): exactly three active algorithms —
ML-KEM-768, ML-DSA-65, SLH-DSA-SHA2-128s. ML-KEM-512 and ML-KEM-1024
(valid FIPS 203 parameter sets) are deliberately OUT of the PR2 scope:
re-adding them requires either explicit test-matrix coverage or a new
specification cycle. HQC and FN-DSA remain on the watchlist.

Architectural boundary (spec v1.2, section 2 / G4):
    HALE/HSL context is transcript metadata and/or protocol-level
    domain-separation input; it is NOT an input to the ML-KEM primitive
    and is NOT cryptographic entropy.

Security note (spec v1.2, section 2): this module provides standardized
NIST algorithms through a documented liboqs backend, within the scope and
limitations of this implementation. It is NOT a cryptographically
validated implementation and does NOT imply that the Hubstry Security
platform as a whole is cryptographically validated.

Author: Hubstry Deep Tech
License: CC BY-NC-SA 4.0
"""

from __future__ import annotations

import hashlib
import hmac
from dataclasses import dataclass
from typing import Literal, Optional

try:  # package import (hyphen-less layouts) or same-directory import
    from . import oqs_adapter as _backend  # type: ignore
except ImportError:  # pragma: no cover - layout dependent
    import oqs_adapter as _backend  # type: ignore

# --------------------------------------------------------------------------
# Algorithm registry (spec v1.2, sections 5, 9, 10)
# --------------------------------------------------------------------------

AlgType = Literal["KEM", "SIG"]
AlgStatus = Literal["active", "optional", "watchlist"]


@dataclass(frozen=True)
class AlgorithmEntry:
    identifier: str          # backend-independent FIPS identifier
    alg_type: AlgType
    nist_standard: str       # e.g. "FIPS 203"
    status: AlgStatus        # watchlist = hard-blocked this cycle
    nist_category: int       # claimed NIST security category
    sizes: dict              # asserted at provider init (fail-fast, T5)
    note: str = ""


# PR2 active scope (review decision, 2026-10): exactly the three algorithms
# below. ML-KEM-512 / ML-KEM-1024 are valid FIPS 203 parameter sets but are
# NOT in the PR2 registry: adding them back requires explicit test-matrix
# coverage or a new specification cycle (future/optional, out of scope).
ALGORITHM_REGISTRY: dict[str, AlgorithmEntry] = {
    "ML-KEM-768": AlgorithmEntry(
        "ML-KEM-768", "KEM", "FIPS 203", "active", 3,
        {"public_key": 1184, "secret_key": 2400, "ciphertext": 1088,
         "shared_secret": 32},
    ),
    "ML-DSA-65": AlgorithmEntry(
        "ML-DSA-65", "SIG", "FIPS 204", "active", 3,
        {"public_key": 1952, "secret_key": 4032, "signature": 3309},
    ),
    "SLH-DSA-SHA2-128s": AlgorithmEntry(
        "SLH-DSA-SHA2-128s", "SIG", "FIPS 205", "active", 1,
        {"public_key": 32, "secret_key": 64, "signature": 7856},
        note="Hash-based alternative (diversity). OQS upstream support "
             "tier recorded in T0 provenance; not a security judgment.",
    ),
    # --- watchlist: hard-blocked in this cycle (spec v1.2, section 10) ---
    "FN-DSA-512": AlgorithmEntry(
        "FN-DSA-512", "SIG", "FIPS 206 (draft)", "watchlist", 1, {},
        note="Draft standard; blocked until FIPS 206 finalization. The "
             "block is tied to standardization state, not to an "
             "independent security judgment by this project.",
    ),
    "HQC-128": AlgorithmEntry(
        "HQC-128", "KEM", "NIST-selected 2025 (standardization upcoming)",
        "watchlist", 1, {},
        note="NIST-selected backup KEM; NOT yet a standard. Roadmap "
             "visibility only; not implemented in PR2.",
    ),
}

DEFAULT_KEM = "ML-KEM-768"
DEFAULT_SIG = "ML-DSA-65"
DEFAULT_KDF = "HKDF-SHA-256"
PROTOCOL_VERSION = "1"
DOMAIN_SEPARATOR = b"hubstry-hsl/v1"


class AlgorithmBlockedError(ValueError):
    """Raised when a watchlist or unknown algorithm is requested."""


def validate_algorithm(identifier: str, expected_type: Optional[AlgType] = None
                       ) -> AlgorithmEntry:
    """Registry validation (T6). Watchlist algorithms are hard-blocked."""
    entry = ALGORITHM_REGISTRY.get(identifier)
    if entry is None:
        raise AlgorithmBlockedError(f"unknown algorithm: {identifier!r}")
    if entry.status == "watchlist":
        raise AlgorithmBlockedError(
            f"algorithm {identifier!r} is on the watchlist and blocked in "
            f"this cycle: {entry.note}"
        )
    if expected_type is not None and entry.alg_type != expected_type:
        raise AlgorithmBlockedError(
            f"algorithm {identifier!r} is a {entry.alg_type}, "
            f"not a {expected_type}"
        )
    return entry


# --------------------------------------------------------------------------
# Normative length-prefixed encoding (spec v1.2, section 6.1 — frozen)
# --------------------------------------------------------------------------

def lp(field: bytes | str) -> bytes:
    """LP(x) = uint32_be(len(x)) || x  (x as UTF-8 bytes).

    Normative, unambiguous composition: plain concatenation of
    variable-length fields is ambiguous (["ab","c"] == ["a","bc"] -> "abc").
    Length-prefixing makes the encoding injective (verified by T10).
    """
    if isinstance(field, str):
        field = field.encode("utf-8")
    return len(field).to_bytes(4, "big") + field


def encode_info(purpose_label: str, hale_context_label: str = "",
                protocol_version: str = PROTOCOL_VERSION,
                kdf_algorithm_id: str = DEFAULT_KDF) -> bytes:
    """Normative HKDF info composition (spec v1.2, section 6.1).

        info = domain_separator
            || LP(protocol_version)
            || LP(purpose_label)
            || LP(HALE_context_label)
            || LP(kdf_algorithm_id)
    """
    return (DOMAIN_SEPARATOR
            + lp(protocol_version)
            + lp(purpose_label)
            + lp(hale_context_label)
            + lp(kdf_algorithm_id))


# --------------------------------------------------------------------------
# HKDF-SHA-256 (RFC 5869) [STANDARDIZED]
# --------------------------------------------------------------------------

def hkdf_extract(salt: bytes, ikm: bytes) -> bytes:
    """HKDF-Extract (RFC 5869 section 2.2)."""
    if not salt:
        salt = b"\x00" * hashlib.sha256().digest_size
    return hmac.new(salt, ikm, hashlib.sha256).digest()


def hkdf_expand(prk: bytes, info: bytes, length: int = 32) -> bytes:
    """HKDF-Expand (RFC 5869 section 2.3), L <= 255 * HashLen."""
    hash_len = hashlib.sha256().digest_size
    if length > 255 * hash_len:
        raise ValueError("HKDF length too large")
    okm, t, counter = b"", b"", 1
    while len(okm) < length:
        t = hmac.new(prk, t + info + bytes([counter]), hashlib.sha256).digest()
        okm += t
        counter += 1
    return okm[:length]


# --------------------------------------------------------------------------
# Canonical transcript (spec v1.2, gate G3 — frozen field order)
# --------------------------------------------------------------------------

TRANSCRIPT_FIELDS = (
    "domain_separator", "protocol_version", "kem_algorithm_id",
    "sig_algorithm_id", "kdf_algorithm_id", "hale_context_label",
    "kem_public_key", "kem_ciphertext", "nonce",
)


def canonical_transcript(*, kem_algorithm_id: str, sig_algorithm_id: str,
                         kdf_algorithm_id: str, hale_context_label: str,
                         kem_public_key: bytes, kem_ciphertext: bytes,
                         nonce: bytes,
                         protocol_version: str = PROTOCOL_VERSION) -> bytes:
    """Canonical, versioned, domain-separated transcript encoding.

    Fixed field order (TRANSCRIPT_FIELDS), every field length-prefixed via
    lp(). Any field substitution, omission, algorithm substitution or
    context-label substitution changes the byte string (T9a-T9e).
    """
    parts = {
        "domain_separator": DOMAIN_SEPARATOR,
        "protocol_version": protocol_version,
        "kem_algorithm_id": kem_algorithm_id,
        "sig_algorithm_id": sig_algorithm_id,
        "kdf_algorithm_id": kdf_algorithm_id,
        "hale_context_label": hale_context_label,
        "kem_public_key": kem_public_key,
        "kem_ciphertext": kem_ciphertext,
        "nonce": nonce,
    }
    return b"".join(lp(parts[name]) for name in TRANSCRIPT_FIELDS)


def transcript_hash(transcript: bytes) -> bytes:
    return hashlib.sha256(transcript).digest()


# --------------------------------------------------------------------------
# Provider facade (G1)
# --------------------------------------------------------------------------

@dataclass
class Keypair:
    public_key: bytes
    secret_key: bytes


class PQCProvider:
    """Crypto-agile PQC provider (spec v1.2, section 5).

    The provider owns algorithm selection/validation, key lifecycle,
    serialization, input validation, transcript binding and backend
    metadata. Its API is NOT a mirror of the liboqs-python internal
    lifecycle; the liboqs adapter is an implementation detail.
    """

    def __init__(self, kem: str = DEFAULT_KEM, sig: str = DEFAULT_SIG,
                 kdf: str = DEFAULT_KDF,
                 protocol_version: str = PROTOCOL_VERSION) -> None:
        self.kem_entry = validate_algorithm(kem, "KEM")
        self.sig_entry = validate_algorithm(sig, "SIG")
        if kdf != DEFAULT_KDF:
            raise AlgorithmBlockedError(
                f"unsupported KDF {kdf!r}; only {DEFAULT_KDF!r} is "
                "specified in PR2 v1.2"
            )
        self.kdf = kdf
        self.protocol_version = protocol_version
        self._kem = _backend.OqsKemAdapter(self.kem_entry.identifier)
        self._sig = _backend.OqsSigAdapter(self.sig_entry.identifier)
        self._assert_sizes()

    def _assert_sizes(self) -> None:
        """Fail-fast size assertions against FIPS constants (T5)."""
        pk, sk = self._kem.generate_keypair()
        ct, ss = self._kem.encapsulate(pk)
        exp = self.kem_entry.sizes
        assert len(pk) == exp["public_key"], "KEM pk size"
        assert len(sk) == exp["secret_key"], "KEM sk size"
        assert len(ct) == exp["ciphertext"], "KEM ct size"
        assert len(ss) == exp["shared_secret"], "KEM ss size"
        spk, ssk = self._sig.generate_keypair()
        sgn = self._sig.sign(b"size-probe", ssk)
        sexp = self.sig_entry.sizes
        assert len(spk) == sexp["public_key"], "SIG pk size"
        assert len(ssk) == sexp["secret_key"], "SIG sk size"
        assert len(sgn) == sexp["signature"], "SIG sig size"

    # --- key lifecycle -------------------------------------------------
    def generate_kem_keypair(self) -> Keypair:
        pk, sk = self._kem.generate_keypair()
        return Keypair(pk, sk)

    def generate_sig_keypair(self) -> Keypair:
        pk, sk = self._sig.generate_keypair()
        return Keypair(pk, sk)

    # --- KEM -----------------------------------------------------------
    def encapsulate(self, public_key: bytes) -> tuple[bytes, bytes]:
        if len(public_key) != self.kem_entry.sizes["public_key"]:
            raise ValueError("KEM public_key length mismatch")
        return self._kem.encapsulate(public_key)

    def decapsulate(self, ciphertext: bytes, secret_key: bytes) -> bytes:
        """Return the shared-secret CANDIDATE (FIPS 203 implicit rejection).

        A returned value may exist even under rejection; it is never a
        session key without protocol authentication / transcript binding
        (spec v1.2, T4). Callers MUST authenticate the transcript.
        """
        if len(ciphertext) != self.kem_entry.sizes["ciphertext"]:
            raise ValueError("KEM ciphertext length mismatch")
        return self._kem.decapsulate(ciphertext, secret_key)

    # --- KDF / key schedule (G2, frozen composition) --------------------
    def derive_session_key(self, shared_secret: bytes, transcript: bytes,
                           purpose_label: str,
                           hale_context_label: str = "",
                           length: int = 32) -> bytes:
        """HKDF-SHA-256: salt = transcript_hash, ikm = shared_secret,
        info = normative encode_info(...), L = length (spec v1.2, 6.1).

        The session key is bound to the FULL canonical transcript via the
        HKDF salt (verified by test_t10_session_key_transcript_binding).
        """
        prk = hkdf_extract(transcript_hash(transcript), shared_secret)
        info = encode_info(purpose_label, hale_context_label,
                           self.protocol_version, self.kdf)
        return hkdf_expand(prk, info, length)

    # --- transcript + signatures ---------------------------------------
    def build_transcript(self, *, kem_public_key: bytes, kem_ciphertext: bytes,
                         nonce: bytes, hale_context_label: str = "") -> bytes:
        return canonical_transcript(
            kem_algorithm_id=self.kem_entry.identifier,
            sig_algorithm_id=self.sig_entry.identifier,
            kdf_algorithm_id=self.kdf,
            hale_context_label=hale_context_label,
            kem_public_key=kem_public_key, kem_ciphertext=kem_ciphertext,
            nonce=nonce, protocol_version=self.protocol_version)

    def sign_transcript(self, transcript: bytes, secret_key: bytes) -> bytes:
        return self._sig.sign(transcript, secret_key)

    def verify_transcript(self, transcript: bytes, signature: bytes,
                          public_key: bytes) -> bool:
        return self._sig.verify(transcript, signature, public_key)

    # --- provenance (T0) -------------------------------------------------
    def backend_metadata(self) -> dict:
        return _backend.backend_metadata(sorted(ALGORITHM_REGISTRY))
