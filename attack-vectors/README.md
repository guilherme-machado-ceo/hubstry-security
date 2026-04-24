# Attack Vectors

## [PT-BR] Catálogo de Vetores de Ataque | [EN] Attack Vector Catalog

---

## Metodologia / Methodology

Este catálogo classifica ameaças com base no **ENISA Threat Landscape 2025** e **OWASP Top 10 2025**, mapeando cada vetor contra os módulos de defesa da Hubstry Security Platform.

This catalog classifies threats based on **ENISA Threat Landscape 2025** and **OWASP Top 10 2025**, mapping each vector against Hubstry Security Platform defense modules.

---

## Vetores Catalogados / Cataloged Vectors

### AV-001: Quantum Brute Force / Força Bruta Quântica

| Campo | Detalhe |
|-------|---------|
| **Tipo** | Criptográfico / Cryptographic |
| **Fonte** | Shor''s Algorithm (1994), NIST PQC Migration Guide |
| **Impacto** | Crítico — quebra RSA/ECC |
| **Mitigação Hubstry** | ML-KEM-768 (FIPS 203) + ML-DSA-65 (FIPS 204) |
| **Status** | Mitigado no design |

Computadores quânticos suficientemente poderosos podem resolver o problema do logaritmo discreto em tempo polinomial, comprometendo RSA e ECC. A Hubstry Security Platform utiliza exclusivamente algoritmos pós-quânticos (baseados em lattice e hash) que permanecem seguros contra ataques quânticos conhecidos.

---

### AV-002: Man-in-the-Middle (MITM)

| Campo | Detalhe |
|-------|---------|
| **Tipo** | Rede / Network |
| **Fonte** | ENISA TL 2025, CWE-300 |
| **Impacto** | Alto — interceptação de dados em trânsito |
| **Mitigação Hubstry** | HSL + ML-DSA-65 mutual authentication |
| **Status** | Mitigado no design |

---

### AV-003: Replay Attack

| Campo | Detalhe |
|-------|---------|
| **Tipo** | Protocolo / Protocol |
| **Fonte** | CWE-294, OWASP 2025 |
| **Impacto** | Médio — reenvio de pacotes válidos |
| **Mitigação Hubstry** | Nonce (32 bytes) + timestamp com janela de 60s |
| **Status** | Mitigado no design |

---

### AV-004: Side-Channel Attack

| Campo | Detalhe |
|-------|---------|
| **Tipo** | Implementação / Implementation |
| **Fonte** | ENISA TL 2025, CWE-208 |
| **Impacto** | Alto — vazamento de chaves via timing/power |
| **Mitigação Hubstry** | Constant-time arithmetic, HSM para f0 |
| **Status** | Planejado para TRL 5 |

---

### AV-005: Supply Chain Attack

| Campo | Detalhe |
|-------|---------|
| **Tipo** | Software / Software |
| **Fonte** | ENISA TL 2025, SolarWinds (2020) |
| **Impacto** | Crítico — comprometimento via dependências |
| **Mitigação Hubstry** | SBOM, assinatura de artefatos, pinning de dependências |
| **Status** | Planejado para TRL 5 |

---

### AV-006: DDoS

| Campo | Detalhe |
|-------|---------|
| **Tipo** | Rede / Network |
| **Fonte** | ENISA TL 2025 |
| **Impacto** | Alto — indisponibilidade de serviço |
| **Mitigação Hubstry** | Rate limiting por canal harmônico, spectral filtering |
| **Status** | Pesquisa |

---

### AV-007: Phishing / Social Engineering

| Campo | Detalhe |
|-------|---------|
| **Tipo** | Humano / Human |
| **Fonte** | ENISA TL 2025, OWASP 2025 |
| **Impacto** | Alto — comprometimento de credenciais |
| **Mitigação Hubstry** | HSL elimina necessidade de credenciais tradicionais |
| **Status** | Mitigado no design (parcial) |

---

### AV-008: Zero-Day Exploits

| Campo | Detalhe |
|-------|---------|
| **Tipo** | Software / Software |
| **Fonte** | CWE-0, ENISA TL 2025 |
| **Impacto** | Crítico — vulnerabilidade desconhecida |
| **Mitigação Hubstry** | Segmentação espectral (contenção), behavioral monitoring |
| **Status** | Pesquisa |

---

### AV-009: Ransomware

| Campo | Detalhe |
|-------|---------|
| **Tipo** | Malware |
| **Fonte** | ENISA TL 2025 |
| **Impacto** | Crítico — criptografia de dados por atacante |
| **Mitigação Hubstry** | PQC encryption at rest, backup harmônico, incident response |
| **Status** | Mitigado no design |

---

### AV-010: DNS Spoofing / Cache Poisoning

| Campo | Detalhe |
|-------|---------|
| **Tipo** | Rede / Network |
| **Fonte** | CWE-406 |
| **Impacto** | Alto — redirecionamento de tráfego |
| **Mitigação Hubstry** | HSL identity verification independente de DNS |
| **Status** | Mitigado no design |

---

### AV-011: Insider Threat

| Campo | Detalhe |
|-------|---------|
| **Tipo** | Humano / Human |
| **Fonte** | ENISA TL 2025 |
| **Impacto** | Alto — ameaça interna |
| **Mitigação Hubstry** | HSM-protected f0, audit trail, role-based channels |
| **Status** | Planejado para TRL 5 |

---

### AV-012: SQL Injection

| Campo | Detalhe |
|-------|---------|
| **Tipo** | Aplicação / Application |
| **Fonte** | OWASP 2025, CWE-89 |
| **Impacto** | Alto — exfiltração de dados |
| **Mitigação Hubstry** | Parameterized queries, input validation, WAF |
| **Status** | Boas práticas |

---

### AV-013: Cross-Site Scripting (XSS)

| Campo | Detalhe |
|-------|---------|
| **Tipo** | Aplicação / Application |
| **Fonte** | OWASP 2025, CWE-79 |
| **Impacto** | Médio — execução de scripts maliciosos |
| **Mitigação Hubstry** | CSP headers, output encoding, sanitization |
| **Status** | Boas práticas |

---

### AV-014: Cryptographic Implementation Flaw

| Campo | Detalhe |
|-------|---------|
| **Tipo** | Criptográfico / Cryptographic |
| **Fonte** | CWE-327, CWE-328 |
| **Impacto** | Crítico — uso de algoritmos fracos |
| **Mitigação Hubstry** | Exclusivamente PQC (FIPS 203/204/205), sem fallback clássico |
| **Status** | Mitigado no design |

---

## Matriz de Risco / Risk Matrix

```
Impacto
  Crítico | AV-001  AV-005  AV-009  AV-014
  Alto    | AV-002  AV-004  AV-006  AV-007  AV-008  AV-010  AV-011  AV-012
  Médio   | AV-003  AV-013
          +-----------------------------------------------
          |     Mitigado    Planejado    Pesquisa
```

---

## Checklist de Verificação / Verification Checklist

Antes de cada release / Before each release:

- [ ] Todos os vetores críticos possuem mitigação implementada
- [ ] Teste de regressão contra novos CVEs publicados (última semana)
- [ ] Benchmark HSL handshake < 1ms (P99)
- [ ] PQC signature verification < 5ms (P99)
- [ ] Review do SBOM para dependências atualizadas
- [ ] Incident response playbook atualizado

---

*Hubstry Deep Tech — Threat Intelligence Module*