# Attack Vectors

## [PT-BR] Cat\u00e1logo de Vetores de Ataque | [EN] Attack Vector Catalog

---

## Metodologia / Methodology

Este cat\u00e1logo classifica amea\u00e7as com base no **ENISA Threat Landscape 2025** e **OWASP Top 10 2025**, mapeando cada vetor contra os m\u00f3dulos de defesa da Hubstry Security Platform.

This catalog classifies threats based on **ENISA Threat Landscape 2025** and **OWASP Top 10 2025**, mapping each vector against Hubstry Security Platform defense modules.

---

## Vetores Catalogados / Cataloged Vectors

### AV-001: Quantum Brute Force / For\u00e7a Bruta Qu\u00e2ntica

| Campo | Detalhe |
|-------|---------|
| **Tipo** | Criptogr\u00e1fico / Cryptographic |
| **Fonte** | Shor''s Algorithm (1994), NIST PQC Migration Guide |
| **Impacto** | Cr\u00edtico \u2014 quebra RSA/ECC |
| **Mitiga\u00e7\u00e3o Hubstry** | ML-KEM-768 (FIPS 203) + ML-DSA-65 (FIPS 204) |
| **Status** | Mitigado no design |

Computadores qu\u00e2nticos suficientemente poderosos podem resolver o problema do logaritmo discreto em tempo polinomial, comprometendo RSA e ECC. A Hubstry Security Platform utiliza exclusivamente algoritmos p\u00f3s-qu\u00e2nticos (baseados em lattice e hash) que permanecem seguros contra ataques qu\u00e2nticos conhecidos.

---

### AV-002: Man-in-the-Middle (MITM)

| Campo | Detalhe |
|-------|---------|
| **Tipo** | Rede / Network |
| **Fonte** | ENISA TL 2025, CWE-300 |
| **Impacto** | Alto \u2014 intercepta\u00e7\u00e3o de dados em tr\u00e2nsito |
| **Mitiga\u00e7\u00e3o Hubstry** | HSL + ML-DSA-65 mutual authentication |
| **Status** | Mitigado no design |

---

### AV-003: Replay Attack

| Campo | Detalhe |
|-------|---------|
| **Tipo** | Protocolo / Protocol |
| **Fonte** | CWE-294, OWASP 2025 |
| **Impacto** | M\u00e9dio \u2014 reenvio de pacotes v\u00e1lidos |
| **Mitiga\u00e7\u00e3o Hubstry** | Nonce (32 bytes) + timestamp com janela de 60s |
| **Status** | Mitigado no design |

---

### AV-004: Side-Channel Attack

| Campo | Detalhe |
|-------|---------|
| **Tipo** | Implementa\u00e7\u00e3o / Implementation |
| **Fonte** | ENISA TL 2025, CWE-208 |
| **Impacto** | Alto \u2014 vazamento de chaves via timing/power |
| **Mitiga\u00e7\u00e3o Hubstry** | Constant-time arithmetic, HSM para f0 |
| **Status** | Planejado para TRL 5 |

---

### AV-005: Supply Chain Attack

| Campo | Detalhe |
|-------|---------|
| **Tipo** | Software / Software |
| **Fonte** | ENISA TL 2025, SolarWinds (2020) |
| **Impacto** | Cr\u00edtico \u2014 comprometimento via depend\u00eancias |
| **Mitiga\u00e7\u00e3o Hubstry** | SBOM, assinatura de artefatos, pinning de depend\u00eancias |
| **Status** | Planejado para TRL 5 |

---

### AV-006: DDoS

| Campo | Detalhe |
|-------|---------|
| **Tipo** | Rede / Network |
| **Fonte** | ENISA TL 2025 |
| **Impacto** | Alto \u2014 indisponibilidade de servi\u00e7o |
| **Mitiga\u00e7\u00e3o Hubstry** | Rate limiting por canal harm\u00f4nico, spectral filtering |
| **Status** | Pesquisa |

---

### AV-007: Phishing / Social Engineering

| Campo | Detalhe |
|-------|---------|
| **Tipo** | Humano / Human |
| **Fonte** | ENISA TL 2025, OWASP 2025 |
| **Impacto** | Alto \u2014 comprometimento de credenciais |
| **Mitiga\u00e7\u00e3o Hubstry** | HSL elimina necessidade de credenciais tradicionais |
| **Status** | Mitigado no design (parcial) |

---

### AV-008: Zero-Day Exploits

| Campo | Detalhe |
|-------|---------|
| **Tipo** | Software / Software |
| **Fonte** | CWE-0, ENISA TL 2025 |
| **Impacto** | Cr\u00edtico \u2014 vulnerabilidade desconhecida |
| **Mitiga\u00e7\u00e3o Hubstry** | Segmenta\u00e7\u00e3o espectral (conten\u00e7\u00e3o), behavioral monitoring |
| **Status** | Pesquisa |

---

### AV-009: Ransomware

| Campo | Detalhe |
|-------|---------|
| **Tipo** | Malware |
| **Fonte** | ENISA TL 2025 |
| **Impacto** | Cr\u00edtico \u2014 criptografia de dados por atacante |
| **Mitiga\u00e7\u00e3o Hubstry** | PQC encryption at rest, backup harm\u00f4nico, incident response |
| **Status** | Mitigado no design |

---

### AV-010: DNS Spoofing / Cache Poisoning

| Campo | Detalhe |
|-------|---------|
| **Tipo** | Rede / Network |
| **Fonte** | CWE-406 |
| **Impacto** | Alto \u2014 redirecionamento de tr\u00e1fego |
| **Mitiga\u00e7\u00e3o Hubstry** | HSL identity verification independente de DNS |
| **Status** | Mitigado no design |

---

### AV-011: Insider Threat

| Campo | Detalhe |
|-------|---------|
| **Tipo** | Humano / Human |
| **Fonte** | ENISA TL 2025 |
| **Impacto** | Alto \u2014 amea\u00e7a interna |
| **Mitiga\u00e7\u00e3o Hubstry** | HSM-protected f0, audit trail, role-based channels |
| **Status** | Planejado para TRL 5 |

---

### AV-012: SQL Injection

| Campo | Detalhe |
|-------|---------|
| **Tipo** | Aplica\u00e7\u00e3o / Application |
| **Fonte** | OWASP 2025, CWE-89 |
| **Impacto** | Alto \u2014 exfiltra\u00e7\u00e3o de dados |
| **Mitiga\u00e7\u00e3o Hubstry** | Parameterized queries, input validation, WAF |
| **Status** | Boas pr\u00e1ticas |

---

### AV-013: Cross-Site Scripting (XSS)

| Campo | Detalhe |
|-------|---------|
| **Tipo** | Aplica\u00e7\u00e3o / Application |
| **Fonte** | OWASP 2025, CWE-79 |
| **Impacto** | M\u00e9dio \u2014 execu\u00e7\u00e3o de scripts maliciosos |
| **Mitiga\u00e7\u00e3o Hubstry** | CSP headers, output encoding, sanitization |
| **Status** | Boas pr\u00e1ticas |

---

### AV-014: Cryptographic Implementation Flaw

| Campo | Detalhe |
|-------|---------|
| **Tipo** | Criptogr\u00e1fico / Cryptographic |
| **Fonte** | CWE-327, CWE-328 |
| **Impacto** | Cr\u00edtico \u2014 uso de algoritmos fracos |
| **Mitiga\u00e7\u00e3o Hubstry** | Exclusivamente PQC (FIPS 203/204/205), sem fallback cl\u00e1ssico |
| **Status** | Mitigado no design |

---

## Matriz de Risco / Risk Matrix

```
Impacto
  Cr\u00edtico | AV-001  AV-005  AV-009  AV-014
  Alto    | AV-002  AV-004  AV-006  AV-007  AV-008  AV-010  AV-011  AV-012
  M\u00e9dio   | AV-003  AV-013
          +-----------------------------------------------
          |     Mitigado    Planejado    Pesquisa
```

---

## Checklist de Verifica\u00e7\u00e3o / Verification Checklist

Antes de cada release / Before each release:

- [ ] Todos os vetores cr\u00edticos possuem mitiga\u00e7\u00e3o implementada
- [ ] Teste de regress\u00e3o contra novos CVEs publicados (\u00faltima semana)
- [ ] Benchmark HSL handshake < 1ms (P99)
- [ ] PQC signature verification < 5ms (P99)
- [ ] Review do SBOM para depend\u00eancias atualizadas
- [ ] Incident response playbook atualizado

---

*Hubstry Deep Tech \u2014 Threat Intelligence Module*