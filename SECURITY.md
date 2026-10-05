# Security Policy

## [PT-BR] Política de Segurança | [EN] Security Policy

---

## Versions Supported / Versões Suportadas

| Versão | Status |
|--------|--------|
| main   | Suportada / Supported |
| develop| Suportada / Supported |

---

## [PT-BR] Reportando Vulnerabilidades | [EN] Reporting Vulnerabilities

### PT-BR

A Hubstry leva a segurança a sério. Se você identificar uma vulnerabilidade, reporte de forma responsável:

1. **Não** abra uma issue pública
2. Envie um email para **guilhermemachado.ceo@hubstry.dev** com assunto `[SECURITY] Vulnerabilidade`
3. Inclua: descrição, impacto potencial, passos para reproduzir e sugestão de mitigação
4. Você receberá confirmação em até 48h (úteis)
5. O timeline de correção será comunicado em até 72h

### EN

Hubstry takes security seriously. If you identify a vulnerability, report it responsibly:

1. **Do not** open a public issue
2. Send an email to **guilhermemachado.ceo@hubstry.dev** with subject `[SECURITY] Vulnerability`
3. Include: description, potential impact, reproduction steps, and suggested mitigation
4. You will receive acknowledgment within 48 business hours
5. A remediation timeline will be communicated within 72 hours

---

## [PT-BR] Rota Pós-Quântica | [EN] Post-Quantum Roadmap

| Padrão / Standard | Status |
|-------------------|--------|
| NIST FIPS 203 (ML-KEM / Kyber) | Provedor experimental na `main` (PR #5, 2026-10-05); não usado por fluxos da plataforma |
| NIST FIPS 204 (ML-DSA / Dilithium) | Provedor experimental na `main` (PR #5, 2026-10-05); integração ao HSL pendente (F-01b) |
| NIST FIPS 205 (SLH-DSA / SPHINCS+) | Provedor experimental na `main` (PR #5, 2026-10-05); não usado por fluxos da plataforma |
| TLS 1.3 + PQC Hybrid | Pesquisa |

Consulte [`post-quantum/`](post-quantum/) para a pesquisa pós-quântica. A integração HALE + PQC é objetivo de pesquisa e não está implementada.

---

*Hubstry Deep Tech — Security Policy*