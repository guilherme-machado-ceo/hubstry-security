# Compliance

## [PT-BR] Mapeamento Regulat\u00f3rio Multi-Framework | [EN] Multi-Framework Regulatory Mapping

---

## Frameworks Mapeados / Mapped Frameworks

| Framework | Jurisdi\u00e7\u00e3o / Jurisdiction | Vers\u00e3o |
|-----------|--------------------------|--------|
| **ENISA NIS2** | Uni\u00e3o Europeia / European Union | Directive 2022/2555 |
| **LGPD** | Brasil | Lei 13.709/2018 |
| **NIST CSF** | Estados Unidos (global ref.) | v2.0 (2024) |
| **ISO 27001** | Internacional | 2022 |
| **OWASP ASVS** | Internacional (web/app) | v4.0 |

---

## ENISA NIS2 \u2014 Medidas de Seguran\u00e7a / Security Measures

| Artigo / Article | Requisito | Mapeamento Hubstry |
|-----------------|-----------|-------------------|
| Art. 21(2)(a) | Pol\u00edticas de seguran\u00e7a de rede | docs/architecture.md, SECURITY.md |
| Art. 21(2)(b) | Treinamento de seguran\u00e7a | roadmap/2026-2027.md (Fase 1) |
| Art. 21(2)(c) | Prote\u00e7\u00e3o contra incidentes | attack-vectors/ (14 vetores mapeados) |
| Art. 21(2)(d) | Continuidade de opera\u00e7\u00f5es | compliance/ (playbook P1-P4) |
| Art. 21(2)(g) | Criptografia em tr\u00e2nsito | PQC Module (ML-KEM-768 + AES-256-GCM) |
| Art. 21(2)(h) | Seguran\u00e7a da cadeia de suprimentos | SBOM, signed artifacts |
| Art. 21(2)(i) | Autentica\u00e7\u00e3o multifator | HSL coherence token + ML-DSA-65 |

---

## LGPD \u2014 Lei Geral de Prote\u00e7\u00e3o de Dados

| Artigo | Requisito | Mapeamento Hubstry |
|--------|-----------|-------------------|
| Art. 46 | Seguran\u00e7a t\u00e9cnica | PQC encryption at rest + in transit |
| Art. 48 | Registro de opera\u00e7\u00f5es | Audit trail por canal harm\u00f4nico |
| Art. 49 | Notifica\u00e7\u00e3o de incidentes | Incident response playbook (P1: 15min) |

---

## NIST CSF 2.0 \u2014 Core Functions

| Function | Categoria | Mapeamento Hubstry |
|----------|----------|-------------------|
| **GOVERN** | GV.OC | Pol\u00edticas de governan\u00e7a em SECURITY.md |
| **IDENTIFY** | ID.AM | HALE node registry (harmonic addressing) |
| **PROTECT** | PR.AA | HSL authentication + ML-DSA-65 |
| **DETECT** | DE.CM | Threat Intel (14 attack vectors monitorados) |
| **RESPOND** | RS.RP | Incident response playbook P1-P4 |
| **RECOVER** | RC.RP | Backup harm\u00f4nico, recovery procedures |

---

## ISO 27001:2022 \u2014 Controles Selecionados

| Controle | Nome | Mapeamento Hubstry |
|----------|------|-------------------|
| A.5.1 | Pol\u00edticas de seguran\u00e7a da informa\u00e7\u00e3o | SECURITY.md |
| A.8.2 | Privil\u00e9gios de acesso | HSM-protected f0, role-based channels |
| A.8.24 | Uso de criptografia | PQC Module (FIPS 203/204/205) |
| A.8.25 | Desenvolvimento seguro | SBOM, signed artifacts |
| A.8.16 | Monitoramento de atividades | Audit trail por canal harm\u00f4nico |
| A.5.24 | Gest\u00e3o de incidentes | Incident response playbook P1-P4 |

---

## Playbook de Resposta a Incidentes | Incident Response Playbook

### Classifica\u00e7\u00e3o por Severidade / Severity Classification

| N\u00edvel / Level | Tempo de Resposta / Response Time | Exemplos |
|---------------|----------------------------------|---------|
| **P1 \u2014 Cr\u00edtico** | 15 minutos | Breach de dados, ransomware ativo, comprometimento de f0 |
| **P2 \u2014 Alto** | 1 hora | Ataque DDoS em progresso, vulnerabilidade zero-day exploitable |
| **P3 \u2014 M\u00e9dio** | 4 horas | Tentativa de intrus\u00e3o detectada, anomalia de autentica\u00e7\u00e3o |
| **P4 \u2014 Baixo** | 24 horas | Falha de integridade de log, alerta de scanner |

### Procedimento P1 / P1 Procedure

```
T+0min:   Alerta autom\u00e1tico -> canal on-call
T+5min:   Triage -> confirma\u00e7\u00e3o do incidente
T+15min:  Conten\u00e7\u00e3o -> isolamento do canal harm\u00f4nico afetado
T+30min:  Comunica\u00e7\u00e3o -> notifica\u00e7\u00e3o a partes interessadas (LGPD Art. 48)
T+1h:     An\u00e1lise forense -> coleta de evid\u00eancias
T+4h:     Erradica\u00e7\u00e3o -> patch/aplica\u00e7\u00e3o de corre\u00e7\u00e3o
T+8h:     Recovery -> restaura\u00e7\u00e3o do servi\u00e7o
T+24h:    Post-mortem -> relat\u00f3rio de li\u00e7\u00f5es aprendidas
```

---

## Editais Brasileiros Relevantes / Relevant Brazilian Calls

| Edital / Call | \u00d3rg\u00e3o | Status |
|---------------|-------|--------|
| CISSA Chamada de Ciberseguran\u00e7a 2025 | CISSA/EMBRAPII/CESAR | Submetido |
| MCTI Chamada CNPq PQ | MCTI/CNPq | Planejado |
| FAPESP PIPE | FAPESP | Planejado |
| BNDES Funtec | BNDES | Planejado |

---

## Refer\u00eancias / References

1. Directive (EU) 2022/2555 \u2014 NIS2 Directive
2. Lei 13.709/2018 \u2014 LGPD
3. NIST CSF 2.0 \u2014 Cybersecurity Framework (2024)
4. ISO/IEC 27001:2022 \u2014 Information Security Management
5. OWASP ASVS v4.0 \u2014 Application Security Verification Standard

---

*Hubstry Deep Tech \u2014 Compliance Module*