# Arquitetura da Plataforma | Platform Architecture

## [PT-BR] Visão Geral

> **Arquitetura-alvo.** Este documento descreve a arquitetura pretendida da plataforma. O estado de implementação de cada componente está indicado abaixo e detalhado em [`research/hsl-documentation-audit-2026-10.md`](research/hsl-documentation-audit-2026-10.md).

A Hubstry Security Platform é organizada como um framework modular onde cada componente opera de forma independente mas compartilha o **HALE Core** — o framework matemático que originou a investigação sobre hierarquias de chaves e tokens de coerência harmônica.

### Componentes Principais

1. **HALE Core** — Motor matemático baseado na Harmonic Addressing & Labeling Equation. Propõe utilizar subdivisões harmônicas racionais de uma frequência fundamental f0 para derivar endereços, chaves criptográficas e tokens de autenticação. A função totiente de Euler phi(b) é aplicada para construir hierarquias de chaves multinível. *Status: proposta de pesquisa; hierarquia de chaves não implementada na `main`.*

2. **PQC Module** — Prevê os três padrões NIST pós-quânticos (FIPS 203, 204, 205) e operações híbridas (clássico + PQ) durante o período de transição. *Status: provedor experimental em revisão no PR #5; ainda não integrado à `main`. A integração com o HALE Core para derivação de chaves é objetivo de pesquisa.*

3. **HSL Engine** — Harmonic Security Layer. Propõe handshakes de autenticação baseados em coerência harmônica. O projeto explorou uma meta de aproximadamente 200 bytes para o handshake completo (challenge + response + verification); esse valor não foi validado experimentalmente. *Status: hipótese de pesquisa; simulação em `hsl/hsl_module.py` com assinatura placeholder.*

4. **Threat Intel** — Catálogo de vetores de ataque atualizado contra ENISA Threat Landscape 2025 e OWASP Top 10 2025. Inclui checklists de verificação e mapeamento de mitigações.

5. **Compliance Engine** — Mapeamento multi-framework de requisitos regulatórios com playbook automatizado de resposta a incidentes (P1-P4).

### Fluxo de Dados

```
Cliente/Node  -->  HSL Engine  -->  HALE Core  -->  PQC Module
                       |               |               |
                  Coherence        Key Hierarchy    ML-KEM-768
                  Token            (phi-based)     ML-DSA-65
                  (hipótese)       (proposta)      (PR #5)
                                                       |
                                              Compliance Engine
                                              (audit log + metrics)
```

### Modelo de Segurança

A plataforma adota os princípios de **Zero Trust** e **Defense in Depth**:

- Nunca confie, sempre verifique (coherence token + PQC signature)
- Segmentação espectral natural (cada canal harmônico opera como micro-segmento)
- Criptografia em repouso e em trânsito (PQC híbrido)
- Resposta a incidentes com SLA definido (P1: 15min, P2: 1h, P3: 4h, P4: 24h)

---

## [EN] Overview

The Hubstry Security Platform is organized as a modular framework where each component operates independently but shares the **HALE Core** — the mathematical framework that started the investigation into key hierarchies and harmonic coherence tokens.

### Core Components

1. **HALE Core** — Mathematical engine based on the Harmonic Addressing & Labeling Equation. Proposes using rational harmonic subdivisions of a fundamental frequency f0 to derive addresses, cryptographic keys, and authentication tokens. Euler''s totient function phi(b) is applied to construct multilevel key hierarchies. *Status: research proposal; key hierarchy not implemented on `main`.*

2. **PQC Module** — Targets the three NIST post-quantum standards (FIPS 203, 204, 205) and hybrid operations (classical + PQ) during the transition period. *Status: experimental provider under review in PR #5; not yet merged into `main`. Integration with the HALE Core for key derivation is a research objective.*

3. **HSL Engine** — Harmonic Security Layer. Proposes authentication handshakes based on harmonic coherence. The project explored a target of approximately 200 bytes for the complete handshake (challenge + response + verification); this value has not been experimentally validated. *Status: research hypothesis; simulation in `hsl/hsl_module.py` with a placeholder signature.*

4. **Threat Intel** — Attack vector catalog updated against ENISA Threat Landscape 2025 and OWASP Top 10 2025. Includes verification checklists and mitigation mapping.

5. **Compliance Engine** — Multi-framework regulatory requirement mapping with automated incident response playbook (P1-P4).

---

## TRL Progression

| Phase | TRL | Focus |
|-------|-----|-------|
| Current | **3** | Proof of concept — mathematical validation + reference implementation |
| TBD (original: Q2 2026) | 4 | Laboratory validation — benchmarks vs TLS 1.3, controlled testing |
| TBD (original: Q3 2026) | 5 | Controlled environment — PoC with validation partner |
| TBD (original: Q1 2027) | 6 | Pilot demonstration — field testing in production-like environment |

---

*Hubstry Deep Tech — 2023-2026*