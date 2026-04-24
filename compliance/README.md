# Compliance

## [PT-BR] Mapeamento Regulatorio Multi-Framework | [EN] Multi-Framework Regulatory Mapping

---

## Frameworks Mapeados / Mapped Frameworks

| Framework | Jurisdicao / Jurisdiction | Versao |
|-----------|--------------------------|--------|
| **ENISA NIS2** | Uniao Europeia / European Union | Directive 2022/2555 |
| **LGPD** | Brasil | Lei 13.709/2018 |
| **NIST CSF** | Estados Unidos (global ref.) | v2.0 (2024) |
| **ISO 27001** | Internacional | 2022 |
| **OWASP ASVS** | Internacional (web/app) | v4.0 |

---

## ENISA NIS2 - Medidas de Seguranca / Security Measures

| Artigo / Article | Requisito | Mapeamento Hubstry |
|-----------------|-----------|-------------------|
| Art. 21(2)(a) | Politicas de seguranca de rede | docs/architecture.md, SECURITY.md |
| Art. 21(2)(b) | Treinamento de seguranca | roadmap/2025-2026.md (Fase 1) |
| Art. 21(2)(c) | Protecao contra incidentes | attack-vectors/ (14 vetores mapeados) |
| Art. 21(2)(d) | Continuidade de operacoes | compliance/ (playbook P1-P4) |
| Art. 21(2)(g) | Criptografia em transito | PQC Module (ML-KEM-768 + AES-256-GCM) |
| Art. 21(2)(h) | Seguranca da cadeia de suprimentos | SBOM, signed artifacts |
| Art. 21(2)(i) | Autenticacao multifator | HSL coherence token + ML-DSA-65 |

---

## LGPD - Lei Geral de Protecao de Dados

| Artigo | Requisito | Mapeamento Hubstry |
|--------|-----------|-------------------|
| Art. 46 | Seguranca tecnica | PQC encryption at rest + in transit |
| Art. 48 | Registro de operacoes | Audit trail por canal harmonico |
| Art. 49 | Notificacao de incidentes | Incident response playbook (P1: 15min) |

---

## NIST CSF 2.0 - Core Functions

| Function | Categoria | Mapeamento Hubstry |
|----------|----------|-------------------|
| **GOVERN** | GV.OC | Politicas de governanca em SECURITY.md |
| **IDENTIFY** | ID.AM | HALE node registry (harmonic addressing) |
| **PROTECT** | PR.AA | HSL authentication + ML-DSA-65 |
| **DETECT** | DE.CM | Threat Intel (14 attack vectors monitorados) |
| **RESPOND** | RS.RP | Incident response playbook P1-P4 |
| **RECOVER** | RC.RP | Backup harmonico, recovery procedures |

---

## ISO 27001:2022 - Controles Selecionados

| Controle | Nome | Mapeamento Hubstry |
|----------|------|-------------------|
| A.5.1 | Politicas de seguranca da informacao | SECURITY.md |
| A.8.2 | Privilegios de acesso | HSM-protected f0, role-based channels |
| A.8.24 | Uso de criptografia | PQC Module (FIPS 203/204/205) |
| A.8.25 | Desenvolvimento seguro | SBOM, signed artifacts |
| A.8.16 | Monitoramento de atividades | Audit trail por canal harmonico |
| A.5.24 | Gestao de incidentes | Incident response playbook P1-P4 |

---

## Playbook de Resposta a Incidentes | Incident Response Playbook

### Classificacao por Severidade / Severity Classification

| Nivel / Level | Tempo de Resposta / Response Time | Exemplos |
|---------------|----------------------------------|---------|
| **P1 - Critico** | 15 minutos | Breach de dados, ransomware ativo, comprometimento de f0 |
| **P2 - Alto** | 1 hora | Ataque DDoS em progresso, vulnerabilidade zero-day exploitable |
| **P3 - Medio** | 4 horas | Tentativa de intrusao detectada, anomalia de autenticacao |
| **P4 - Baixo** | 24 horas | Falha de integridade de log, alerta de scanner |

### Procedimento P1 / P1 Procedure

```
T+0min:   Alerta automatico -> canal on-call
T+5min:   Triage -> confirmacao do incidente
T+15min:  Contencao -> isolamento do canal harmonico afetado
T+30min:  Comunicacao -> notificacao a partes interessadas (LGPD Art. 48)
T+1h:     Analise forense -> coleta de evidencias
T+4h:     Eradicacao -> patch/aplicacao de correcao
T+8h:     Recovery -> restauracao do servico
T+24h:    Post-mortem -> relatorio de licoes aprendidas
```

---

## Editais Brasileiros Relevantes | Relevant Brazilian Calls

| Edital / Call | Orgao | Status |
|---------------|-------|--------|
| CISSA Chamada de Ciberseguranca 2025 | CISSA/EMBRAPII/CESAR | Submetido |
| MCTI Chamada CNPq PQ | MCTI/CNPq | Planejado |
| FAPESP PIPE | FAPESP | Planejado |
| BNDES Funtec | BNDES | Planejado |

---

## Referencias / References

1. Directive (EU) 2022/2555 - NIS2 Directive
2. Lei 13.709/2018 - LGPD
3. NIST CSF 2.0 - Cybersecurity Framework (2024)
4. ISO/IEC 27001:2022 - Information Security Management
5. OWASP ASVS v4.0 - Application Security Verification Standard

---

*Hubstry Deep Tech - Compliance Module*