"""
PR2 test suite T0-T10 (spec v1.2, section 11).

Classification: these tests verify USAGE of standardized NIST algorithms
through the documented liboqs backend, within scope. They do not validate
the liboqs internals and imply no whole-platform cryptographic validation.

Scope note (review, 2026-10): the PR2 registry contains exactly three
active algorithms (ML-KEM-768, ML-DSA-65, SLH-DSA-SHA2-128s). Test
coverage targets this set; ML-KEM-512/1024 are out of PR2 scope.

T4 scope note: T4 is a PRE-Digital-Twin property test. It verifies that a
tampered ciphertext breaks transcript authentication; it does NOT
implement a full two-party handshake with session accept/reject rules.
Full handshake accept/reject validation belongs to the Digital
Laboratory Twin phase.

Run: python -m pytest tests/pqc/ -q
"""

from __future__ import annotations

import hashlib
import hmac as _hmac
import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "post-quantum"))

import pqc_provider as pqc  # noqa: E402

# Backend policy: without liboqs the suite is skipped locally. When
# HUBSTRY_REQUIRE_PQC=1 (set in CI), a missing backend is a failure, so a
# skipped suite can never be read as a passing one.
_BACKEND_AVAILABLE = pqc._backend.backend_available()
if not _BACKEND_AVAILABLE and os.environ.get("HUBSTRY_REQUIRE_PQC") == "1":
    raise RuntimeError(
        "HUBSTRY_REQUIRE_PQC=1 but the liboqs backend is unavailable; "
        "the PQC suite must not be skipped in this environment"
    )

pytestmark = pytest.mark.skipif(
    not _BACKEND_AVAILABLE,
    reason="liboqs backend unavailable in this environment",
)


@pytest.fixture(scope="module")
def provider():
    return pqc.PQCProvider()  # ML-KEM-768 + ML-DSA-65, HKDF-SHA-256


@pytest.fixture(scope="module")
def provider_slh():
    return pqc.PQCProvider(sig="SLH-DSA-SHA2-128s")


# --- T0: backend provenance/capability (G5) -------------------------------
def test_t0_provenance(provider):
    meta = provider.backend_metadata()
    for key in ("liboqs_python_version", "oqs_version", "python_version",
                "platform", "algorithms"):
        assert key in meta and meta[key] not in (None, "")
    for alg in ("ML-KEM-768", "ML-DSA-65", "SLH-DSA-SHA2-128s"):
        assert meta["algorithms"][alg]["available"] is True
        assert meta["algorithms"][alg]["identifier"] == alg
    # FN-DSA blocked at registry level (absence/block recorded)
    with pytest.raises(pqc.AlgorithmBlockedError):
        pqc.validate_algorithm("FN-DSA-512")


# --- T1: KEM roundtrip -----------------------------------------------------
def test_t1_kem_roundtrip(provider):
    for _ in range(100):
        kp = provider.generate_kem_keypair()
        ct, ss = provider.encapsulate(kp.public_key)
        assert provider.decapsulate(ct, kp.secret_key) == ss


# --- T2: signature roundtrip ----------------------------------------------
def test_t2_sig_roundtrip(provider):
    kp = provider.generate_sig_keypair()
    messages = [b"", b"a", os.urandom(4096), b"x" * 65536]
    for msg in messages:
        sig = provider.sign_transcript(msg, kp.secret_key)
        assert provider.verify_transcript(msg, sig, kp.public_key) is True


def test_t2_sig_roundtrip_slh(provider_slh):
    kp = provider_slh.generate_sig_keypair()
    sig = provider_slh.sign_transcript(b"slh-test", kp.secret_key)
    assert provider_slh.verify_transcript(b"slh-test", sig, kp.public_key)


# --- T3: negative signature ------------------------------------------------
def test_t3_negative_sig(provider):
    kp = provider.generate_sig_keypair()
    msg, sig = b"msg", provider.sign_transcript(b"msg", kp.secret_key)
    assert provider.verify_transcript(b"msg!", sig, kp.public_key) is False
    bad = bytearray(sig); bad[10] ^= 1
    assert provider.verify_transcript(msg, bytes(bad), kp.public_key) is False
    kp2 = provider.generate_sig_keypair()
    assert provider.verify_transcript(msg, sig, kp2.public_key) is False


# --- T4: negative KEM (G6, v1.2 protocol-level property) -------------------
def test_t4_negative_kem_protocol_level(provider):
    """PRE-Digital-Twin property test (not a full handshake validation).

    A tampered ciphertext MUST NOT result in acceptance of the original
    shared secret as an authenticated session key. Acceptance requires
    transcript authentication; decapsulation errors are not relied upon,
    nor is secret-inequality alone.

    OBSERVED scope of this test: altering the ciphertext alters the
    canonical transcript and invalidates the corresponding signature.
    A full two-party handshake with explicit ACCEPT/REJECT session rules
    is NOT implemented here; that validation belongs to the Digital
    Laboratory Twin phase.
    """
    sig_kp = provider.generate_sig_keypair()
    kem_kp = provider.generate_kem_keypair()
    ct, ss = provider.encapsulate(kem_kp.public_key)
    nonce = os.urandom(16)
    transcript = provider.build_transcript(
        kem_public_key=kem_kp.public_key, kem_ciphertext=ct, nonce=nonce)
    signature = provider.sign_transcript(transcript, sig_kp.secret_key)

    bad_ct = bytearray(ct); bad_ct[0] ^= 1
    # Observational only: compute the implicit-rejection candidate for
    # evidence/debugging, but do not assert any relation to the original
    # shared secret. FIPS 203 does not make secret inequality the protocol
    # acceptance criterion.
    candidate = provider.decapsulate(bytes(bad_ct), kem_kp.secret_key)
    assert candidate is not None

    # protocol level: tampered ct breaks transcript verification
    bad_transcript = provider.build_transcript(
        kem_public_key=kem_kp.public_key, kem_ciphertext=bytes(bad_ct),
        nonce=nonce)
    assert provider.verify_transcript(bad_transcript, signature,
                                      sig_kp.public_key) is False
    # even with the candidate, no authenticated session key is accepted
    assert provider.verify_transcript(transcript, signature,
                                      sig_kp.public_key) is True


# --- T5: size assertions (also run at provider init, fail-fast) ------------
def test_t5_sizes(provider):
    e = pqc.ALGORITHM_REGISTRY["ML-KEM-768"].sizes
    kp = provider.generate_kem_keypair()
    ct, ss = provider.encapsulate(kp.public_key)
    assert (len(kp.public_key), len(kp.secret_key), len(ct), len(ss)) == (
        e["public_key"], e["secret_key"], e["ciphertext"], e["shared_secret"])
    se = pqc.ALGORITHM_REGISTRY["ML-DSA-65"].sizes
    skp = provider.generate_sig_keypair()
    s = provider.sign_transcript(b"m", skp.secret_key)
    assert (len(skp.public_key), len(skp.secret_key), len(s)) == (
        se["public_key"], se["secret_key"], se["signature"])


# --- T6: registry / watchlist rejection ------------------------------------
def test_t6_registry():
    with pytest.raises(pqc.AlgorithmBlockedError):
        pqc.PQCProvider(sig="FN-DSA-512")
    with pytest.raises(pqc.AlgorithmBlockedError):
        pqc.PQCProvider(kem="HQC-128")
    with pytest.raises(pqc.AlgorithmBlockedError):
        pqc.PQCProvider(kem="Kyber-1024")   # unknown identifier
    with pytest.raises(pqc.AlgorithmBlockedError):
        pqc.validate_algorithm("ML-DSA-65", "KEM")  # wrong type
    # PR2 scope control: ML-KEM-512/1024 are out of this cycle's registry
    for out_of_scope in ("ML-KEM-512", "ML-KEM-1024"):
        with pytest.raises(pqc.AlgorithmBlockedError):
            pqc.validate_algorithm(out_of_scope)


# --- T7: crypto-agility swap ------------------------------------------------
def test_t7_agility():
    for kem, sig in (("ML-KEM-768", "ML-DSA-65"),
                     ("ML-KEM-768", "SLH-DSA-SHA2-128s")):
        p = pqc.PQCProvider(kem=kem, sig=sig)
        kp = p.generate_kem_keypair()
        ct, ss = p.encapsulate(kp.public_key)
        assert p.decapsulate(ct, kp.secret_key) == ss
        skp = p.generate_sig_keypair()
        s = p.sign_transcript(b"m", skp.secret_key)
        assert p.verify_transcript(b"m", s, skp.public_key) is True
        bad = bytearray(s); bad[0] ^= 1
        assert p.verify_transcript(b"m", bytes(bad), skp.public_key) is False


# --- T8: environment record (G7: reproducibility vs determinism) -----------
def test_t8_environment_record(provider):
    meta = provider.backend_metadata()
    required = {"liboqs_python_version", "oqs_version", "python_version",
                "platform", "algorithms"}
    assert required <= set(meta), "incomplete environment/provenance record"


# --- T9: canonical transcript (G3) ------------------------------------------
def _tr(provider, **kw):
    base = dict(kem_public_key=b"P" * 1184, kem_ciphertext=b"C" * 1088,
                nonce=b"N" * 16, hale_context_label="node-A")
    base.update(kw)
    return provider.build_transcript(**base)


def test_t9a_canonical_serialization(provider):
    assert _tr(provider) == _tr(provider)  # byte-identical


def test_t9b_field_substitution(provider):
    sig_kp = provider.generate_sig_keypair()
    t = _tr(provider)
    s = provider.sign_transcript(t, sig_kp.secret_key)
    t2 = _tr(provider, nonce=b"M" * 16)
    assert t2 != t
    assert provider.verify_transcript(t2, s, sig_kp.public_key) is False


def test_t9c_field_omission(provider):
    t = _tr(provider)
    # an omission is not re-parseable to the same transcript
    assert len(_tr(provider, nonce=b"")) != len(t)
    assert _tr(provider, nonce=b"") != t


def test_t9d_algorithm_substitution(provider):
    sig_kp = provider.generate_sig_keypair()
    t = _tr(provider)
    s = provider.sign_transcript(t, sig_kp.secret_key)
    other = pqc.canonical_transcript(
        kem_algorithm_id="ML-KEM-1024", sig_algorithm_id="ML-DSA-65",
        kdf_algorithm_id="HKDF-SHA-256", hale_context_label="node-A",
        kem_public_key=b"P" * 1184, kem_ciphertext=b"C" * 1088,
        nonce=b"N" * 16)
    assert other != t
    assert provider.verify_transcript(other, s, sig_kp.public_key) is False


def test_t9e_context_label_substitution(provider):
    sig_kp = provider.generate_sig_keypair()
    t = _tr(provider, hale_context_label="node-A")
    s = provider.sign_transcript(t, sig_kp.secret_key)
    t2 = _tr(provider, hale_context_label="node-B")
    assert provider.verify_transcript(t2, s, sig_kp.public_key) is False


# --- T10: KDF (RFC 5869 vectors + domain separation + info injectivity) ----
def test_t10_hkdf_rfc5869_vector():
    # RFC 5869 Test Case 1 (SHA-256)
    ikm = bytes.fromhex("0b" * 22)
    salt = bytes.fromhex("000102030405060708090a0b0c")
    info = bytes.fromhex("f0f1f2f3f4f5f6f7f8f9")
    prk = pqc.hkdf_extract(salt, ikm)
    assert prk.hex() == ("077709362c2e32df0ddc3f0dc47bba63"
                         "90b6c73bb50f9c3122ec844ad7c2b3e5")
    okm = pqc.hkdf_expand(prk, info, 42)
    assert okm.hex() == ("3cb25f25faacd57a90434f64d0362f2a"
                         "2d2d0a90cf1a5a4c5db02d56ecc4c5bf"
                         "34007208d5b887185865")


def test_t10_domain_separation(provider):
    kp = provider.generate_kem_keypair()
    ct, ss = provider.encapsulate(kp.public_key)
    t = provider.build_transcript(kem_public_key=kp.public_key,
                                  kem_ciphertext=ct, nonce=b"n" * 16)
    k1 = provider.derive_session_key(ss, t, "enc")
    k2 = provider.derive_session_key(ss, t, "mac")
    k3 = provider.derive_session_key(ss, t, "enc",
                                     hale_context_label="other-ctx")
    assert k1 != k2 != k3 and len(k1) == 32


def test_t10_session_key_transcript_binding(provider):
    """The session key is bound to the FULL canonical transcript.

    The transcript hash is the HKDF salt, so the derived key must change
    whenever ANY transcript field changes — even with identical shared
    secret, purpose label and context label. This is a central
    architectural property of the v1.2 key schedule.
    """
    kp = provider.generate_kem_keypair()
    ct, ss = provider.encapsulate(kp.public_key)
    base = dict(kem_public_key=kp.public_key, kem_ciphertext=ct,
                nonce=b"n" * 16, hale_context_label="node-A")
    t_a = provider.build_transcript(**base)
    key_a = provider.derive_session_key(ss, t_a, "enc")

    # sanity: identical inputs reproduce the identical key
    assert provider.derive_session_key(ss, t_a, "enc") == key_a

    variants = [
        dict(base, nonce=b"m" * 16),                    # nonce changed
        dict(base, kem_ciphertext=bytes([ct[0] ^ 1]) + ct[1:]),  # ct changed
        dict(base, kem_public_key=bytes([kp.public_key[0] ^ 1])
            + kp.public_key[1:]),                        # pk changed
        dict(base, hale_context_label="node-B"),         # context changed
    ]
    for v in variants:
        t_b = provider.build_transcript(**v)
        assert t_b != t_a
        key_b = provider.derive_session_key(ss, t_b, "enc")
        assert key_b != key_a, "session key not bound to full transcript"


def test_t10_info_encoding_injective():
    """Length-prefixed info: distinct field tuples never collide."""
    seen = {}
    versions = ["1", "11"]
    purposes = ["enc", "en", "c", "mac", "resumption"]
    ctxs = ["", "a", "ab", "node-A"]
    kdfs = ["HKDF-SHA-256"]
    for v in versions:
        for pur in purposes:
            for ctx in ctxs:
                for k in kdfs:
                    blob = pqc.encode_info(pur, ctx, v, k)
                    key = (v, pur, ctx, k)
                    assert blob not in seen or seen[blob] == key
                    seen[blob] = key
    # the classic ambiguity case must NOT collide
    assert pqc.encode_info("ab", "c") != pqc.encode_info("a", "bc")


# --- Hardening (PR #5 review, item 2): explicit size-check exception --------
def test_size_mismatch_raises_explicit_exception(provider):
    """_assert_sizes raises BackendSizeMismatchError (not AssertionError)."""
    import dataclasses
    wrong = dict(provider.kem_entry.sizes, public_key=1)
    original = provider.kem_entry
    try:
        provider.kem_entry = dataclasses.replace(original, sizes=wrong)
        with pytest.raises(pqc.BackendSizeMismatchError, match="KEM public_key"):
            provider._assert_sizes()
    finally:
        provider.kem_entry = original
