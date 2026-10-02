"""
liboqs adapter — thin internal wrapper (PR2, spec v1.2, G1)
===========================================================

This module is an IMPLEMENTATION DETAIL of the PQCProvider facade.
Application code must not import it directly; use
``post-quantum/pqc_provider.py``. The adapter is swappable and the
provider's tests run against the provider interface, not against
liboqs internals (spec v1.2, gate G1).

Responsibilities (only):
    - lazy import of liboqs-python with actionable error
    - raw KEM/SIG operations
    - backend provenance/capability metadata (T0)

Algorithm identifiers used here are the FIPS-standard names and are
backend-independent: ``algorithm identifier != backend version !=
library version`` (spec v1.2, section 13).

Author: Hubstry Deep Tech
License: CC BY-NC-SA 4.0
"""

from __future__ import annotations

import platform
from typing import Optional

# Backend name mapping (spec v1.2, section 13): the registry identifier is
# backend-independent; the backend's internal string may differ (e.g.
# liboqs 0.16 uses "SLH_DSA_PURE_SHA2_128S"). Mapping lives ONLY here.
_BACKEND_NAME = {
    "ML-KEM-768": "ML-KEM-768",
    "ML-KEM-512": "ML-KEM-512",
    "ML-KEM-1024": "ML-KEM-1024",
    "ML-DSA-65": "ML-DSA-65",
    "SLH-DSA-SHA2-128s": "SLH_DSA_PURE_SHA2_128S",
}


def _backend_alg(identifier: str) -> str:
    """Map a backend-independent identifier to the liboqs mechanism name."""
    return _BACKEND_NAME.get(identifier, identifier)


_IMPORT_ERROR: Optional[str] = None
try:
    import oqs  # type: ignore
except Exception as exc:  # pragma: no cover - environment dependent
    oqs = None  # type: ignore
    _IMPORT_ERROR = str(exc)


def backend_available() -> bool:
    """True if liboqs-python and the native liboqs library are usable."""
    if oqs is None:
        return False
    try:
        oqs.KeyEncapsulation(_backend_alg("ML-KEM-768"))
        return True
    except Exception:
        return False


def require_backend() -> None:
    """Raise with install instructions if the liboqs backend is unusable."""
    if backend_available():
        return
    raise RuntimeError(
        "liboqs backend unavailable"
        + (f" (import error: {_IMPORT_ERROR})" if _IMPORT_ERROR else "")
        + ". Install with: pip install liboqs-python "
        "(requires CMake >= 3.26 and a C compiler to build liboqs; "
        "see https://github.com/open-quantum-safe/liboqs-python)."
    )


def backend_metadata(algorithms: list[str]) -> dict:
    """T0 provenance/capability record (spec v1.2, section 11).

    Records library versions, per-algorithm availability and the exact
    identifiers the backend exposes. Availability is probed, never assumed.
    """
    require_backend()
    import importlib.metadata as md

    def _ver(dist: str) -> str:
        try:
            return md.version(dist)
        except md.PackageNotFoundError:
            return "not-installed"

    enabled_kems = set(oqs.get_enabled_kem_mechanisms())
    enabled_sigs = set(oqs.get_enabled_sig_mechanisms())
    per_algo = {}
    for name in algorithms:
        bname = _backend_alg(name)
        per_algo[name] = {
            "available": bname in enabled_kems or bname in enabled_sigs,
            "identifier": name,
            "backend_mechanism": bname,
        }
    return {
        "liboqs_python_version": _ver("liboqs-python"),
        "oqs_version": getattr(oqs, "OQS_VERSION", "unknown"),
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "algorithms": per_algo,
    }


class OqsKemAdapter:
    """Raw KEM operations via liboqs. Internal use only (G1)."""

    def __init__(self, algorithm: str) -> None:
        require_backend()
        self.algorithm = _backend_alg(algorithm)

    def generate_keypair(self) -> tuple[bytes, bytes]:
        with oqs.KeyEncapsulation(self.algorithm) as kem:
            public_key = kem.generate_keypair()
            return bytes(public_key), bytes(kem.export_secret_key())

    def encapsulate(self, public_key: bytes) -> tuple[bytes, bytes]:
        with oqs.KeyEncapsulation(self.algorithm) as kem:
            ciphertext, shared_secret = kem.encap_secret(public_key)
            return bytes(ciphertext), bytes(shared_secret)

    def decapsulate(self, ciphertext: bytes, secret_key: bytes) -> bytes:
        with oqs.KeyEncapsulation(self.algorithm, secret_key) as kem:
            return bytes(kem.decap_secret(ciphertext))


class OqsSigAdapter:
    """Raw signature operations via liboqs. Internal use only (G1)."""

    def __init__(self, algorithm: str) -> None:
        require_backend()
        self.algorithm = _backend_alg(algorithm)

    def generate_keypair(self) -> tuple[bytes, bytes]:
        with oqs.Signature(self.algorithm) as sig:
            public_key = sig.generate_keypair()
            return bytes(public_key), bytes(sig.export_secret_key())

    def sign(self, message: bytes, secret_key: bytes) -> bytes:
        with oqs.Signature(self.algorithm, secret_key) as sig:
            return bytes(sig.sign(message))

    def verify(self, message: bytes, signature: bytes, public_key: bytes) -> bool:
        with oqs.Signature(self.algorithm) as sig:
            return bool(sig.verify(message, signature, public_key))
