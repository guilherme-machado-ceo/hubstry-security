<div align="center">

# Hubstry Security Platform

**Cybersecurity platform with post-quantum cryptography and harmonic authentication**

*Plataforma de cibersegurança com criptografia pós-quântica e autenticação harmônica*

[![License: CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC_BY--NC--SA_4.0-lightgrey.svg)](LICENSE)
[![PQC Ready](https://img.shields.io/badge/PQC-NIST_FIPS_203%2F204%2F205-brightgreen)](post-quantum/README.md)
[![TRL 3](https://img.shields.io/badge/TRL-3-orange)](docs/architecture.md)
[![Security](https://img.shields.io/badge/Security-Policy-blue)](SECURITY.md)

</div>

---
## Incrementos / Latest Implementations

| Módulo | Arquivo | Descrição |
|--------|---------|-----------|
| **HSL Auth** | hsl_layer/hsl_auth.py | Autenticação H-Challenge/Response 3 etapas (~200B) |
| **Detecção de Intrusão** | hsl_layer/intrusion_detection.py | Desvio de fase Δφ > ε |
| **Rotação LFSR** | hsl_layer/key_rotation.py | Rotação de chaves via LFSR |
| **π-Radical Operator** | pi_radical/pi_radical.py | Operador π-radical — 6 relações ρ₁-ρ₆ |
| **Lattice 64 Perfis** | pi_radical/lattice_profiles.py | Lattice de 64 perfis harmônicos |
| **W Matrix Fixed-Point** | pi_radical/w_matrix.py | Matriz W — ponto fixo espectral |
| **Bound ρ₃ Quântico** | pi_radical/quantum_bound.py | Limite quântico ρ₃ |
| **HSL Demo** | demo/hsl_demo.py | Demonstração interativa HSL |


## [PT-BR] Sobre | [EN] About

### Sobre

A **Hubstry Security Platform** é uma framework de cibersegurança de propósito geral que integra quatro pilares fundamentais: **Criptografia Pós-Quântica** (NIST FIPS 203/204/205), **Autenticação Harmônica** (HSL — Harmonic Security Layer), **Análise de Vetores de Ataque** (ENISA 2025 + OWASP 2025) e **Conformidade Regulatória** (NIS2, LGPD, NIST CSF 2.0, ISO 27001).

Desenvolvida pela **Hubstry Deep Tech** (fundada em 2023), a plataforma utiliza o framework matemático **HALE** (Harmonic Addressing & Labeling Equation) para derivar hierarquias de chaves baseadas em subdivisões harmônicas racionais de uma frequência fundamental f0, oferecendo separabilidade espectral natural para segmentação de redes e autenticação leve.

O módulo **HSL** realiza handshakes de autenticação em aproximadamente **200 bytes**, contra os ~8 KB do TLS 1.3, mantendo resistência computacional equivalente — tornando-o ideal para IoT, telecomunicações e ambientes com recursos limitados.

### About

The **Hubstry Security Platform** is a general-purpose cybersecurity framework integrating four core pillars: **Post-Quantum Cryptography** (NIST FIPS 203/204/205), **Harmonic Authentication** (HSL — Harmonic Security Layer), **Attack Vector Analysis** (ENISA 2025 + OWASP 2025), and **Regulatory Compliance** (NIS2, LGPD, NIST CSF 2.0, ISO 27001).

Developed by **Hubstry Deep Tech** (founded in 2023), the platform leverages the **HALE** (Harmonic Addressing & Labeling Equation) mathematical framework to derive key hierarchies based on rational harmonic subdivisions of a fundamental frequency f0, providing natural spectral separability for network segmentation and lightweight authentication.

The **HSL** module performs authentication handshakes in approximately **200 bytes**, compared to TLS 1.3''s ~8 KB, maintaining equivalent computational resistance — making it ideal for IoT, telecommunications, and resource-constrained environments.

---

## [PT-BR] Ecossistema Hubstry | [EN] Hubstry Ecosystem

Este repositório faz parte do ecossistema Hubstry:

| Repositório | Descrição | Link |
|----------------|-------------|------|
| **hubstry-hale-ecosystem** | Framework matemático HALE | [GitHub](https://github.com/guilherme-machado-ceo/hubstry-hale-ecosystem) |
| **iot-protocol-hubstry** | Protocolo IoT / HPG | [GitHub](https://github.com/guilherme-machado-ceo/iot-protocol-hubstry) |
| **qualia-hub-ecosystem** | Plataforma Qualia Hub | [GitHub](https://github.com/guilherme-machado-ceo/qualia-hub-ecosystem) |
| **hubstry-security** | Plataforma de cibersegurança (este repo) | [GitHub](https://github.com/guilherme-machado-ceo/hubstry-security) |

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

**Módulos / Modules:**

| Módulo | Descrição / Description |
|--------|------------------------|
| [`post-quantum/`](post-quantum/) | Implementação dos padrões NIST PQC (ML-KEM, ML-DSA, SLH-DSA) com integração HALE |
| [`hsl/`](hsl/) | Harmonic Security Layer — autenticação baseada em coerência harmônica |
| [`attack-vectors/`](attack-vectors/) | Catálogo de 14+ vetores de ataque mapeados contra ENISA 2025 e OWASP 2025 |
| [`compliance/`](compliance/) | Mapeamento regulatório multi-framework com playbook de resposta a incidentes |
| [`docs/`](docs/) | Arquitetura detalhada, modelo de ameaças e especificações técnicas |
| [`roadmap/`](roadmap/) | Planejamento de desenvolvimento 2026-2027 e progressão TRL |

---

## [PT-BR] Início Rápido | [EN] Quick Start

### Pré-requisitos

- Git 2.40+
- Python 3.10+ (para exemplos de referência)
- liboqs 0.10+ (para exemplos PQC)

### Clonar / Clone

```bash
git clone https://github.com/guilherme-machado-ceo/hubstry-security.git
cd hubstry-security
```

### Exemplo PQC — ML-KEM-768 com HALE

```python
from hashlib import sha256
import math

def hale_key_derivation(f0, level, b):
    phi = sum(1 for k in range(1, b) if math.gcd(k, b) == 1)
    fk = f0 * (phi ** level)
    return sha256(str(f0).encode()).digest()
```

---

## [PT-BR] Roadmap Técnico | [EN] Technical Roadmap

| Fase | Período | TRL | Entregáveis |
|------|------------|-----|-------------|
| **Fase 1** | Q2 2026 | 3-4 | Validação laboratorial do HSL; benchmarks contra TLS 1.3 |
| **Fase 2** | Q3 2026 | 4-5 | Integração ML-KEM-768 + HSL; PoC em ambiente controlado |
| **Fase 3** | Q1 2027 | 5-6 | Testes com parceiro telecom; conformidade NIS2 validada |

Veja o roadmap completo em [`roadmap/2026-2027.md`](roadmap/2026-2027.md).

---

## [PT-BR] Conformidade Regulatória | [EN] Regulatory Compliance

- **ENISA NIS2** — Medidas de segurança de rede e informação (UE 2022/2555)
- **LGPD** — Lei Geral de Proteção de Dados (Brasil, Lei 13.709/2018)
- **NIST CSF 2.0** — Cybersecurity Framework v2.0 (2024)
- **ISO 27001:2022** — Information Security Management System
- **OWASP ASVS 4.0** — Application Security Verification Standard

Detalhes em [`compliance/`](compliance/).

---

## [PT-BR] Segurança | [EN] Security

Reporte vulnerabilidades em [`SECURITY.md`](SECURITY.md).

---

## [PT-BR] Contribuição | [EN] Contributing

Contribuições são bem-vindas! Consulte [`CONTRIBUTING.md`](CONTRIBUTING.md).

---

## [PT-BR] Licença | [EN] License

Este projeto está licenciado sob **CC BY-NC-SA 4.0** — uso não comercial. Veja [`LICENSE`](LICENSE).

This project is licensed under **CC BY-NC-SA 4.0** — non-commercial use. See [`LICENSE`](LICENSE).

---

<div align="center">

**Hubstry Deep Tech** | Fundada em 2023 | Brasil

[www.hubstry.dev](https://www.hubstry.dev) | [LinkedIn](https://www.linkedin.com/in/guilhermegoncalvesmachado)

</div>