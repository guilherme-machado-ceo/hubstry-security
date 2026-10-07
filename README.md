# Hubstry Security Platform

**Post-quantum cryptography, built on evidence**

*[Portuguese summary: plataforma de cibersegurança para criptografia pós-quântica e pesquisa em segurança harmônica, com desenvolvimento orientado por evidências.]*

[![CI](https://github.com/guilherme-machado-ceo/hubstry-security/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/guilherme-machado-ceo/hubstry-security/actions/workflows/ci.yml)
[![NIST PQC](https://img.shields.io/badge/NIST-FIPS%20203%2F204%2F205-informational)](post-quantum/README.md)
[![License: CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC_BY--NC--SA_4.0-lightgrey.svg)](LICENSE)

---

## The problem

The transition to post-quantum cryptography is an engineering migration problem as much as a cryptographic one. Systems that protect long-lived data today may face a future in which cryptographically relevant quantum computing changes the threat model — the familiar "harvest now, decrypt later" concern.

For constrained systems, the challenge is broader: authentication, key establishment, protocol framing, implementation correctness and reproducibility all have to work together without turning an experimental security claim into a production claim.

## What already works

| Verified project result | Evidence / source |
|---|---|
| Experimental ML-KEM-768, ML-DSA-65 and SLH-DSA-SHA2-128s provider on liboqs 0.16.0, with 19 PQC tests independently reproduced | [PQC reproduction report](docs/research/pr5-pqc-reproduction-report-2026-10.md) |
| HSL Auth v1 experimental handshake using PSK + HMAC-SHA-256, with 32 tests and five mutation defects detected | [HSL v1 execution report](docs/research/hsl-v1-execution-report-2026-10.md) |
| Quantum-research track with 136 tests reproduced across three independent environments | [PR1 research record](docs/research/pr1-quantum-encoding.md) |
| Catalog of 14 attack vectors mapped against ENISA 2025 and OWASP 2025 | [attack-vectors/](attack-vectors/) |
| Regulatory mapping covering NIS2, LGPD, NIST CSF 2.0 and ISO 27001 | [compliance/](compliance/) |

The project does **not** treat the existence of a component as proof of system-level security. Provider-level PQC evidence remains separate from protocol-level integration and laboratory validation.

## Evidence-oriented engineering

The repository uses an explicit evidence discipline:

- **Independent reproduction:** a single-agent experimental result is not promoted to baseline evidence without independent reproduction where technically feasible.
- **Three CI gates:** syntax, general tests, and PQC tests with the required liboqs backend run independently.
- **Status separation:** implementation status, research hypothesis, measured result and validation maturity are documented separately.
- **Review before merge:** technical changes are expected to pass the repository's review and CI gates before entering `main`.

See [CONTRIBUTING.md](CONTRIBUTING.md) for the evidence rule and CI gate definitions.

## Quick start

### Prerequisites

- Git 2.40+
- Python 3.10+
- For the PQC suite: liboqs 0.16.0 and liboqs-python 0.16.0

### Run the general test suite

```bash
python -m pytest tests/ --ignore=tests/pqc -v
```

### Run the PQC suite

```bash
HUBSTRY_REQUIRE_PQC=1 python -m pytest tests/pqc -v
```

The PQC suite requires the liboqs 0.16.0 backend. In CI, an unavailable backend is a failure rather than a skip.

### Run HSL Auth v1

```bash
python hsl/hsl_auth_v1.py
```

HSL Auth v1 is experimental and uses PSK + HMAC-SHA-256. It is not a post-quantum handshake.

## Next milestones

1. **F-01b — ML-DSA integration into HSL:** define and validate the protocol bridge between the experimental HSL handshake and the PQC provider.
2. **Digital Laboratory Twin:** establish a controlled, reproducible environment for system-level protocol validation.
3. **Integrated adversarial validation:** exercise tampering, replay, substitution and other negative protocol scenarios across the integrated system.

These milestones have no new dates assigned. Historical schedule information is preserved in [roadmap/2026-2027.md](roadmap/2026-2027.md).

## Ecosystem and compliance

Hubstry Security is part of the wider Hubstry research ecosystem:

| Repository | Role |
|---|---|
| [hubstry-hale-ecosystem](https://github.com/guilherme-machado-ceo/hubstry-hale-ecosystem) | HALE mathematical framework |
| [iot-protocol-hubstry](https://github.com/guilherme-machado-ceo/iot-protocol-hubstry) | IoT protocol / HPG research |
| [qualia-hub-ecosystem](https://github.com/guilherme-machado-ceo/qualia-hub-ecosystem) | Qualia Hub platform |
| [hubstry-security](https://github.com/guilherme-machado-ceo/hubstry-security) | This cybersecurity research platform |

The repository documents mappings to NIS2, LGPD, NIST CSF 2.0 and ISO 27001 in [compliance/](compliance/).

## Partnerships

We are open to **research and validation partnerships** in post-quantum cryptography, protocol security, constrained systems and security experimentation.

Contact: **guilhermemachado.ceo@hubstry.dev**

## Maturity and limitations

**Current technical status and limitations:** see [`docs/STATUS.md`](docs/STATUS.md).

The system-level **TRL 4 is not established**; component/provider results are tracked separately from protocol and laboratory validation. See [`docs/TRL.md`](docs/TRL.md).

---

**Hubstry Deep Tech** · Brazil · hubstry.dev
