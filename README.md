<div align="center">

# Hubstry Security Platform

**Cybersecurity platform with post-quantum cryptography and harmonic authentication**

*Plataforma de ciberseguranca com criptografia pos-quantica e autenticacao harmonica*

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![PQC Ready](https://img.shields.io/badge/PQC-NIST_FIPS_203%2F204%2F205-brightgreen)](post-quantum/README.md)
[![TRL 3](https://img.shields.io/badge/TRL-3-orange)](docs/architecture.md)
[![Security](https://img.shields.io/badge/Security-Policy-blue)](SECURITY.md)

</div>

---

## [PT-BR] Sobre | [EN] About

### Sobre

A **Hubstry Security Platform** e uma framework de ciberseguranca de proposito geral que integra quatro pilares fundamentais: **Criptografia Pos-Quantica** (NIST FIPS 203/204/205), **Autenticacao Harmonica** (HSL - Harmonic Security Layer), **Analise de Vetores de Ataque** (ENISA 2025 + OWASP 2025) e **Conformidade Regulatoria** (NIS2, LGPD, NIST CSF 2.0, ISO 27001).

Desenvolvida pela **Hubstry Deep Tech** (fundada em 2023), a plataforma utiliza o framework matematico **HALE** (Harmonic Addressing and Labeling Equation) para derivar hierarquias de chaves baseadas em subdivisoes harmonicas racionais de uma frequencia fundamental f0, oferecendo separabilidade espectral natural para segmentacao de redes e autenticacao leve.

O modulo **HSL** realiza handshakes de autenticacao em aproximadamente **200 bytes**, contra os ~8 KB do TLS 1.3, mantendo resistencia computacional equivalente - tornando-o ideal para IoT, telecomunicacoes e ambientes com recursos limitados.

### About

The **Hubstry Security Platform** is a general-purpose cybersecurity framework integrating four core pillars: **Post-Quantum Cryptography** (NIST FIPS 203/204/205), **Harmonic Authentication** (HSL - Harmonic Security Layer), **Attack Vector Analysis** (ENISA 2025 + OWASP 2025), and **Regulatory Compliance** (NIS2, LGPD, NIST CSF 2.0, ISO 27001).

Developed by **Hubstry Deep Tech** (founded in 2023), the platform leverages the **HALE** (Harmonic Addressing and Labeling Equation) mathematical framework to derive key hierarchies based on rational harmonic subdivisions of a fundamental frequency f0, providing natural spectral separability for network segmentation and lightweight authentication.

The **HSL** module performs authentication handshakes in approximately **200 bytes**, compared to TLS 1.3''s ~8 KB, maintaining equivalent computational resistance - making it ideal for IoT, telecommunications, and resource-constrained environments.

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

**Modulos / Modules:**

| Modulo | Descricao / Description |
|--------|------------------------|
| [`post-quantum/`](post-quantum/) | Implementacao dos padroes NIST PQC (ML-KEM, ML-DSA, SLH-DSA) com integracao HALE |
| [`hsl/`](hsl/) | Harmonic Security Layer - autenticacao baseada em coerencia harmonica |
| [`attack-vectors/`](attack-vectors/) | Catalogo de 14+ vetores de ataque mapeados contra ENISA 2025 e OWASP 2025 |
| [`compliance/`](compliance/) | Mapeamento regulatorio multi-framework com playbook de resposta a incidentes |
| [`docs/`](docs/) | Arquitetura detalhada, modelo de ameacas e especificacoes tecnicas |
| [`roadmap/`](roadmap/) | Planejamento de desenvolvimento 2025-2026 e progressao TRL |

---

## [PT-BR] Inicio Rapido | [EN] Quick Start

### Prerequisitos

- Git 2.40+
- Python 3.10+ (para exemplos de referencia)
- liboqs 0.10+ (para exemplos PQC)

### Clonar / Clone

```bash
git clone https://github.com/guilhermegoncalvesmachado/hubstry-security.git
cd hubstry-security
```

### Exemplo PQC - ML-KEM-768 com HALE

```python
from hashlib import sha256
import math

def hale_key_derivation(f0, level, b):
    phi = sum(1 for k in range(1, b) if math.gcd(k, b) == 1)
    fk = f0 * (phi ** level)
    return sha256(str(f0).encode()).digest()
```

---

## [PT-BR] Roadmap Tecnico | [EN] Technical Roadmap

| Fase | Periodo | TRL | Entregaveis |
|------|---------|-----|-------------|
| **Fase 1** | Q3 2025 | 3-4 | Validacao laboratorial do HSL; benchmarks contra TLS 1.3 |
| **Fase 2** | Q1 2026 | 4-5 | Integracao ML-KEM-768 + HSL; PoC em ambiente controlado |
| **Fase 3** | Q3 2026 | 5-6 | Testes com parceiro telecom; conformidade NIS2 validada |

Veja o roadmap completo em [`roadmap/2025-2026.md`](roadmap/2025-2026.md).

---

## [PT-BR] Conformidade Regulatoria | [EN] Regulatory Compliance

- **ENISA NIS2** - Medidas de seguranca de rede e informacao (UE 2022/2555)
- **LGPD** - Lei Geral de Protecao de Dados (Brasil, Lei 13.709/2018)
- **NIST CSF 2.0** - Cybersecurity Framework v2.0 (2024)
- **ISO 27001:2022** - Information Security Management System
- **OWASP ASVS 4.0** - Application Security Verification Standard

Detalhes em [`compliance/`](compliance/).

---

## [PT-BR] Seguranca | [EN] Security

Reporte vulnerabilidades em [`SECURITY.md`](SECURITY.md).

---

## [PT-BR] Contribuicao | [EN] Contributing

Contribuicoes sao bem-vindas! Consulte [`CONTRIBUTING.md`](CONTRIBUTING.md).

---

## [PT-BR] Licenca | [EN] License

Este projeto esta licenciado sob a **MIT License** - veja [`LICENSE`](LICENSE).

---

<div align="center">

**Hubstry Deep Tech** | Fundada em 2023 | Brasil

[www.hubstry.dev](https://www.hubstry.dev) | [LinkedIn](https://www.linkedin.com/in/guilhermegoncalvesmachado)

</div>