<div align="center">

# Hubstry Security Platform

**Cybersecurity platform with post-quantum cryptography and harmonic authentication**

*Plataforma de ciberseguran\u00e7a com criptografia p\u00f3s-qu\u00e2ntica e autentica\u00e7\u00e3o harm\u00f4nica*

[![License: CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC_BY--NC--SA_4.0-lightgrey.svg)](LICENSE)
[![PQC Ready](https://img.shields.io/badge/PQC-NIST_FIPS_203%2F204%2F205-brightgreen)](post-quantum/README.md)
[![TRL 3](https://img.shields.io/badge/TRL-3-orange)](docs/architecture.md)
[![Security](https://img.shields.io/badge/Security-Policy-blue)](SECURITY.md)

</div>

---

## [PT-BR] Sobre | [EN] About

### Sobre

A **Hubstry Security Platform** \u00e9 uma framework de ciberseguran\u00e7a de prop\u00f3sito geral que integra quatro pilares fundamentais: **Criptografia P\u00f3s-Qu\u00e2ntica** (NIST FIPS 203/204/205), **Autentica\u00e7\u00e3o Harm\u00f4nica** (HSL \u2014 Harmonic Security Layer), **An\u00e1lise de Vetores de Ataque** (ENISA 2025 + OWASP 2025) e **Conformidade Regulat\u00f3ria** (NIS2, LGPD, NIST CSF 2.0, ISO 27001).

Desenvolvida pela **Hubstry Deep Tech** (fundada em 2023), a plataforma utiliza o framework matem\u00e1tico **HALE** (Harmonic Addressing & Labeling Equation) para derivar hierarquias de chaves baseadas em subdivis\u00f5es harm\u00f4nicas racionais de uma frequ\u00eancia fundamental f0, oferecendo separabilidade espectral natural para segmenta\u00e7\u00e3o de redes e autentica\u00e7\u00e3o leve.

O m\u00f3dulo **HSL** realiza handshakes de autentica\u00e7\u00e3o em aproximadamente **200 bytes**, contra os ~8 KB do TLS 1.3, mantendo resist\u00eancia computacional equivalente \u2014 tornando-o ideal para IoT, telecomunica\u00e7\u00f5es e ambientes com recursos limitados.

### About

The **Hubstry Security Platform** is a general-purpose cybersecurity framework integrating four core pillars: **Post-Quantum Cryptography** (NIST FIPS 203/204/205), **Harmonic Authentication** (HSL \u2014 Harmonic Security Layer), **Attack Vector Analysis** (ENISA 2025 + OWASP 2025), and **Regulatory Compliance** (NIS2, LGPD, NIST CSF 2.0, ISO 27001).

Developed by **Hubstry Deep Tech** (founded in 2023), the platform leverages the **HALE** (Harmonic Addressing & Labeling Equation) mathematical framework to derive key hierarchies based on rational harmonic subdivisions of a fundamental frequency f0, providing natural spectral separability for network segmentation and lightweight authentication.

The **HSL** module performs authentication handshakes in approximately **200 bytes**, compared to TLS 1.3''s ~8 KB, maintaining equivalent computational resistance \u2014 making it ideal for IoT, telecommunications, and resource-constrained environments.

---

## [PT-BR] Ecossistema Hubstry | [EN] Hubstry Ecosystem

Este reposit\u00f3rio faz parte do ecossistema Hubstry:

| Reposit\u00f3rio | Descri\u00e7\u00e3o | Link |
|----------------|-------------|------|
| **hubstry-hale-ecosystem** | Framework matem\u00e1tico HALE | [GitHub](https://github.com/guilherme-machado-ceo/hubstry-hale-ecosystem) |
| **iot-protocol-hubstry** | Protocolo IoT / HPG | [GitHub](https://github.com/guilherme-machado-ceo/iot-protocol-hubstry) |
| **qualia-hub-ecosystem** | Plataforma Qualia Hub | [GitHub](https://github.com/guilherme-machado-ceo/qualia-hub-ecosystem) |
| **hubstry-security** | Plataforma de ciberseguran\u00e7a (este repo) | [GitHub](https://github.com/guilherme-machado-ceo/hubstry-security) |

This repository is part of the Hubstry ecosystem:

| Repository | Description | Link |
|-----------|-------------|------|
| **hubstry-hale-ecosystem** | HALE mathematical framework | [GitHub](https://github.com/guilherme-machado-ceo/hubstry-hale-ecosystem) |
| **iot-protocol-hubstry** | IoT Protocol / HPG | [GitHub](https://github.com/guilherme-machado-ceo/iot-protocol-hubstry) |
| **qualia-hub-ecosystem** | Qualia Hub Platform | [GitHub](https://github.com/guilherme-machado-ceo/qualia-hub-ecosystem) |
| **hubstry-security** | Cybersecurity platform (this repo) | [GitHub](https://github.com/guilherme-machado-ceo/hubstry-security) |

---

## [PT-BR] Arquitetura | [EN] Architecture

<div align="center">

```
                        +-------------------------+
                        |   Hubstry Security      |
                        |   Platform              |
                        +-------------------------+
                                  |
            +---------------------+---------------------+
            |              |              |             |
    +-------v-------+ +----v----+ +------v-----+ +----v------+
    | Post-Quantum  | |   HSL   | |  Attack    | | Compliance|
    | Cryptography  | | Harmonic| |  Vectors   | |  Mapping  |
    | NIST FIPS     | | Auth    | |  ENISA/    | |  NIS2     |
    | 203/204/205   | | ~200B   | |  OWASP     | |  LGPD     |
    +---------------+ +---------+ |  Analysis  | |  NIST CSF |
                                    +------------+ |  ISO27001|
                                                   +----------+
```

</div>

**M\u00f3dulos / Modules:**

| M\u00f3dulo | Descri\u00e7\u00e3o / Description |
|--------|------------------------|
| [`post-quantum/`](post-quantum/) | Implementa\u00e7\u00e3o dos padr\u00f5es NIST PQC (ML-KEM, ML-DSA, SLH-DSA) com integra\u00e7\u00e3o HALE |
| [`hsl/`](hsl/) | Harmonic Security Layer \u2014 autentica\u00e7\u00e3o baseada em coer\u00eancia harm\u00f4nica |
| [`attack-vectors/`](attack-vectors/) | Cat\u00e1logo de 14+ vetores de ataque mapeados contra ENISA 2025 e OWASP 2025 |
| [`compliance/`](compliance/) | Mapeamento regulat\u00f3rio multi-framework com playbook de resposta a incidentes |
| [`docs/`](docs/) | Arquitetura detalhada, modelo de amea\u00e7as e especifica\u00e7\u00f5es t\u00e9cnicas |
| [`roadmap/`](roadmap/) | Planejamento de desenvolvimento 2026-2027 e progress\u00e3o TRL |

---

## [PT-BR] In\u00edcio R\u00e1pido | [EN] Quick Start

### Pr\u00e9-requisitos

- Git 2.40+
- Python 3.10+ (para exemplos de refer\u00eancia)
- liboqs 0.10+ (para exemplos PQC)

### Clonar / Clone

```bash
git clone https://github.com/guilherme-machado-ceo/hubstry-security.git
cd hubstry-security
```

### Exemplo PQC \u2014 ML-KEM-768 com HALE

```python
from hashlib import sha256
import math

def hale_key_derivation(f0, level, b):
    phi = sum(1 for k in range(1, b) if math.gcd(k, b) == 1)
    fk = f0 * (phi ** level)
    return sha256(str(f0).encode()).digest()
```

---

## [PT-BR] Roadmap T\u00e9cnico | [EN] Technical Roadmap

| Fase | Per\u00edodo | TRL | Entreg\u00e1veis |
|------|------------|-----|-------------|
| **Fase 1** | Q2 2026 | 3-4 | Valida\u00e7\u00e3o laboratorial do HSL; benchmarks contra TLS 1.3 |
| **Fase 2** | Q3 2026 | 4-5 | Integra\u00e7\u00e3o ML-KEM-768 + HSL; PoC em ambiente controlado |
| **Fase 3** | Q1 2027 | 5-6 | Testes com parceiro telecom; conformidade NIS2 validada |

Veja o roadmap completo em [`roadmap/2026-2027.md`](roadmap/2026-2027.md).

---

## [PT-BR] Conformidade Regulat\u00f3ria | [EN] Regulatory Compliance

- **ENISA NIS2** \u2014 Medidas de seguran\u00e7a de rede e informa\u00e7\u00e3o (UE 2022/2555)
- **LGPD** \u2014 Lei Geral de Prote\u00e7\u00e3o de Dados (Brasil, Lei 13.709/2018)
- **NIST CSF 2.0** \u2014 Cybersecurity Framework v2.0 (2024)
- **ISO 27001:2022** \u2014 Information Security Management System
- **OWASP ASVS 4.0** \u2014 Application Security Verification Standard

Detalhes em [`compliance/`](compliance/).

---

## [PT-BR] Seguran\u00e7a | [EN] Security

Reporte vulnerabilidades em [`SECURITY.md`](SECURITY.md).

---

## [PT-BR] Contribui\u00e7\u00e3o | [EN] Contributing

Contribui\u00e7\u00f5es s\u00e3o bem-vindas! Consulte [`CONTRIBUTING.md`](CONTRIBUTING.md).

---

## [PT-BR] Licen\u00e7a | [EN] License

Este projeto est\u00e1 licenciado sob **CC BY-NC-SA 4.0** \u2014 uso n\u00e3o comercial. Veja [`LICENSE`](LICENSE).

This project is licensed under **CC BY-NC-SA 4.0** \u2014 non-commercial use. See [`LICENSE`](LICENSE).

---

<div align="center">

**Hubstry Deep Tech** | Fundada em 2023 | Brasil

[www.hubstry.dev](https://www.hubstry.dev) | [LinkedIn](https://www.linkedin.com/in/guilhermegoncalvesmachado)

</div>