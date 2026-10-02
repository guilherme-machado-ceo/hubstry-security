"""
PR2 CPU benchmark (spec v1.2, sections 12 and 15).

Measures keygen/encaps/decaps/sign/verify latency (median, p95) and message
overhead for the active algorithms, with the full environment metadata block
(G7). No TLS comparison. No security-level inference from timings.

Run: python post-quantum/bench_pqc.py
"""

from __future__ import annotations

import json
import os
import platform
import statistics
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import pqc_provider as pqc  # noqa: E402

WARMUP = 20
ITERATIONS = 1000
TARGET_OP_SECONDS = 2.0  # adaptive: slow ops (e.g. SLH-DSA) get fewer iters


def _time_op(fn, iterations=ITERATIONS):
    # calibrate: measure once, adapt iteration count to TARGET_OP_SECONDS
    t0 = time.perf_counter_ns()
    fn()
    single = (time.perf_counter_ns() - t0) / 1e9
    n = max(5, min(iterations, int(TARGET_OP_SECONDS / max(single, 1e-9))))
    warm = min(WARMUP, max(1, n // 10))
    for _ in range(warm):
        fn()
    samples = []
    for _ in range(n):
        t0 = time.perf_counter_ns()
        fn()
        samples.append((time.perf_counter_ns() - t0) / 1e6)  # ms
    samples.sort()
    return {
        "median_ms": round(statistics.median(samples), 4),
        "p95_ms": round(samples[int(0.95 * len(samples)) - 1], 4),
        "min_ms": round(samples[0], 4),
        "iterations": n,
        "warmup": warm,
    }


def environment_metadata(provider: pqc.PQCProvider) -> dict:
    """G7(a): benchmark reproducibility block (spec v1.2, section 15)."""
    meta = provider.backend_metadata()
    meta.update({
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "cpu": platform.processor() or platform.machine(),
        "cpu_cores": os.cpu_count(),
        "os_kernel": platform.release(),
        "machine": platform.machine(),
        "compiler": os.environ.get("CC", "system-default"),
        "cmake_version": os.environ.get("CMAKE_VERSION", "see build log"),
        "oqs_minimal_build": os.environ.get("OQS_MINIMAL_BUILD", "unset"),
        "note": "G7(b): cryptographic determinism is documented per "
                "algorithm in the spec; no fixed seed substitutes for "
                "this metadata block.",
    })
    return meta


def main() -> None:
    print("=" * 64)
    print("  PR2 PQC CPU benchmark (spec v1.2) - no TLS comparison")
    print("  No security-level inference is made from timings.")
    print("=" * 64)

    report = {"environment": None, "algorithms": {}}

    for kem, sig in (("ML-KEM-768", "ML-DSA-65"),
                     ("ML-KEM-768", "SLH-DSA-SHA2-128s")):
        p = pqc.PQCProvider(kem=kem, sig=sig)
        if report["environment"] is None:
            report["environment"] = environment_metadata(p)

        kem_kp = p.generate_kem_keypair()
        sig_kp = p.generate_sig_keypair()
        ct, _ss = p.encapsulate(kem_kp.public_key)
        msg = os.urandom(256)

        alg = report["algorithms"].setdefault(kem, {})
        alg["keygen"] = _time_op(p.generate_kem_keypair)
        alg["encapsulate"] = _time_op(
            lambda: p.encapsulate(kem_kp.public_key))
        alg["decapsulate"] = _time_op(
            lambda: p.decapsulate(ct, kem_kp.secret_key))
        alg["overhead_bytes"] = {
            "public_key": len(kem_kp.public_key),
            "ciphertext": len(ct), "shared_secret": 32,
        }

        salg = report["algorithms"].setdefault(sig, {})
        salg["keygen"] = _time_op(p.generate_sig_keypair)
        salg["sign"] = _time_op(
            lambda: p.sign_transcript(msg, sig_kp.secret_key))
        sig_bytes = p.sign_transcript(msg, sig_kp.secret_key)
        salg["verify"] = _time_op(
            lambda: p.verify_transcript(msg, sig_bytes, sig_kp.public_key))
        salg["overhead_bytes"] = {
            "public_key": len(sig_kp.public_key),
            "signature": len(sig_bytes),
        }

    out = Path(__file__).resolve().parent / "bench_pqc_results.json"
    out.write_text(json.dumps(report, indent=2))
    print(json.dumps(report["algorithms"], indent=2))
    print(f"\nFull report (with environment metadata) -> {out}")


if __name__ == "__main__":
    main()
