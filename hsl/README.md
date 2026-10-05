# HSL — Harmonic Security Layer

## [PT-BR] Camada de Segurança Harmônica | [EN] Harmonic Security Layer

---

## Conceito / Concept

> **Status: hipótese de pesquisa.** Este documento descreve o desenho do HSL e a sua implementação experimental. Nenhuma propriedade de segurança ou desempenho listada aqui foi validada. Auditoria completa: [`docs/research/hsl-documentation-audit-2026-10.md`](../docs/research/hsl-documentation-audit-2026-10.md).

O **HSL** (Harmonic Security Layer) é uma proposta de protocolo de autenticação leve baseado em **coerência harmônica**, derivada da pesquisa HALE. O projeto explorou uma meta de aproximadamente **200 bytes** por handshake; esse valor não foi validado experimentalmente, e a comparação com o TLS 1.3 ainda não foi medida.

> **Status: research hypothesis.** This document describes the HSL design and its experimental implementation. None of the security or performance properties listed here has been validated.

**HSL** (Harmonic Security Layer) is a proposed lightweight authentication protocol based on **harmonic coherence**, derived from the HALE research. The project explored a target of approximately **200 bytes** per handshake; this value has not been experimentally validated, and the comparison with TLS 1.3 has not been measured.

---

## Protocolo / Protocol

### Fases do Handshake HSL / HSL Handshake Phases

**Desenho histórico (meta de projeto, não corresponde à implementação atual):**

```
  Node A                          Node B
    |                                |
    |  1. CHALLENGE (48 bytes)       |
    |  [fA, nonceA, timestamp]       |
    |------------------------------->|
    |                                |
    |           2. RESPONSE (48 bytes)|
    |           [fB, nonceB,         |
    |            gcd(fA,fB) sig]     |
    |<-------------------------------|
    |                                |
    |  3. VERIFY (104 bytes)         |
    |  [HSL_token, PQC_sign,         |
    |   session_id]                  |
    |------------------------------->|
    |                                |
    |      [ authenticated ]          |
    |                                |
    Total: ~200 bytes (meta histórica)
```

**Implementação atual** ([`hsl_module.py`](hsl_module.py)), medida pela simulação `python3 hsl/hsl_module.py`:

| Etapa | Campos serializados | Tamanho |
|---|---|---|
| 1. Challenge | fase (4 B), nonce (32 B), timestamp (8 B), `node_id` | 44 B + `node_id` |
| 2. Response | fase (4 B), `sigma` SHA-256 (32 B), nonce (32 B), `node_id` | 68 B + `node_id` |
| 3. Verify | token (32 B), assinatura simulada (64 B), `session_id` (16 B), flag (1 B) | 113 B |
| **Total na simulação de referência** | identificadores de 13 e 11 caracteres | **249 B** |

A assinatura da etapa 3 é um placeholder (`SHA-512` truncado em 64 B), não ML-DSA-65. A integração de uma assinatura ML-DSA-65 implicará requisitos de tamanho de mensagem significativamente diferentes, a serem medidos no protocolo efetivamente definido.

---

## Propriedades de Segurança | Security Properties

| Propriedade / Property | Objetivo de desenho | Status na implementação atual |
|----------------------|-----------|-----------|
| **Resistência Quântica** | Composição com ML-DSA-65 (NIST Level 3) no Verify step | Não implementada: assinatura simulada (placeholder) |
| **Replay Protection** | Nonce + timestamp com janela de 60s | Parcial: janela temporal verificada; sem registro de nonces já usados |
| **Forward Secrecy** | Frequências harmônicas derivadas por sessão (ephemeral) | Não implementada: a fase é determinística por `node_id` |
| **Mutual Authentication** | Ambos os nós provam conhecimento de f0 compartilhado | Não implementada: só o respondente produz prova; a etapa 3 não é verificada |
| **Impersonation Resistance** | Hipótese: exigiria resolver um problema difícil no espaço harmônico | Não demonstrada: problema não definido; a aceitação depende apenas de f0 |
| **Liveness** | Timestamp limita a validade das mensagens | Parcial: janela temporal no challenge |

---

## HSL vs TLS 1.3 — Comparação

> **Tabela histórica, não medida.** Os valores do HSL abaixo eram metas de projeto. Nenhum benchmark foi executado. A tabela é mantida como registro e não deve ser citada como resultado.

| Métrica / Metric | HSL (meta histórica) | TLS 1.3 (referência citada) |
|--------------------|-----|---------|
| **Handshake Size** | ~200 bytes (não validado; simulação atual: 249 B) | ~8,000 bytes (valor não especificado) |
| **Reduction** | Não medida | — |
| **Round Trips** | 1.5 RTT | 1 RTT (w/ 0-RTT) |
| **Quantum Resistance** | Planejada (ML-DSA-65); não implementada | Not native (hybrid extension) |
| **Key Exchange** | Harmonic coherence (sem troca de chaves implementada) | ECDH (X25519) |
| **Certificate Size** | Não aplicável ao formato experimental atual | ~2-4 KB (X.509) |
| **CPU (handshake)** | Não medido | Não medido |
| **Memory footprint** | Não medido | Não medido |

> **Diferença de categoria.** O modelo pretendido do HSL é uma configuração ou segredo pré-compartilhado entre as partes; esse modelo ainda não está implementado e não foi validado criptograficamente (ver achado F-03 da auditoria). O TLS 1.3 autentica partes sem segredo prévio, com certificados. As duas construções resolvem problemas diferentes e a comparação direta de tamanho não é equivalente.

> **Nota / Note:** TLS 1.3 continua sendo o padrão para comunicação web generalista. Aplicações-alvo em investigação para o HSL: IoT, telecomunicações, sistemas embarcados e ambientes com recursos computacionais restritos.

---

## Implementação de Referência | Reference Implementation

> **Pseudocódigo histórico, não funcional.** O arquivo `reference-impl/hsl_handshake.py` citado anteriormente não existe. O trecho abaixo concatena `bytes` e `str` (erro de tipo), devolve `"authenticated": True` incondicionalmente e grava `"total_bytes": 200` como constante. A implementação experimental vigente está em [`hsl_module.py`](hsl_module.py).

```python
import hashlib
import math
import time
import secrets

class HSLEngine:
    NONCE_SIZE = 32
    TIMESTAMP_WINDOW = 60

    def __init__(self, node_id, f0=440, base=12):
        self.node_id = node_id
        self.f0 = f0
        self.base = base
        self.frequency = node_id * f0

    @staticmethod
    def _euler_totient(n):
        return sum(1 for k in range(1, n) if math.gcd(k, n) == 1)

    def create_challenge(self):
        return {
            "fA": self.frequency,
            "nonceA": secrets.token_bytes(self.NONCE_SIZE).hex(),
            "timestamp": int(time.time())
        }

    def create_response(self, challenge):
        fB = self.frequency
        gcd_val = math.gcd(challenge["fA"], fB)
        nonce_a = challenge["nonceA"]
        sig_input = str(gcd_val) + ":" + nonce_a + ":" + str(fB)
        return {
            "fB": fB,
            "nonceB": secrets.token_bytes(self.NONCE_SIZE).hex(),
            "gcd_signature": hashlib.sha256(sig_input.encode()).digest()[:8].hex()
        }

    def verify(self, challenge, response):
        fA = challenge["fA"]
        fB = response["fB"]
        gcd_val = math.gcd(fA, fB)
        nonce_a = challenge["nonceA"]
        nonce_b = response["nonceB"]
        coherence_input = str(fA) + ":" + str(fB) + ":" + str(gcd_val) + ":" + nonce_a + ":" + nonce_b
        hsl_token = hashlib.sha256(coherence_input.encode()).digest()
        session_id = hashlib.sha256(hsl_token + str(time.time()).encode()).digest()[:8].hex()
        pq_signature = hashlib.sha512(hsl_token + "PQC:" + str(self.f0) + ":" + str(self.base)).digest()[:64].hex()
        return {
            "hsl_token": hsl_token.hex(),
            "session_id": session_id,
            "authenticated": True,
            "gcd": gcd_val,
            "total_bytes": 200
        }
```

---

## Limitações Conhecidas | Known Limitations

1. **Sem proteção contra MITM ativo** em modo puro — requer canal inicial seguro para troca de f0. A proteção contra MITM é um objetivo do modo híbrido (HSL + PQC), ainda não implementado.
2. **f0 como segredo compartilhado** — se f0 for comprometido, toda a hierarquia é comprometida. Recomenda-se armazenar f0 em HSM.
3. **Benchmark pendente** — nenhum número de tamanho, CPU ou memória foi medido. A validação laboratorial prevista para Q2 2026 (TRL 4) será replanejada.
4. **Autenticação dependente apenas de f0** — na implementação atual, a construção não fornece autenticação criptográfica baseada em segredo quando f0 assume o valor padrão documentado (440 Hz). Ver achado F-03 da auditoria.
5. **Assinatura simulada** — a etapa 3 usa um placeholder no lugar de ML-DSA-65.

---

## Referências | References

1. Diffie, W. and Hellman, M. — New Directions in Cryptography (1976)
2. NIST FIPS 204 — Module-Lattice-Based Digital Signature Standard (2024)
3. RFC 8446 — The Transport Layer Security (TLS) Protocol Version 1.3 (2018)
4. ENISA — Threat Landscape for Smart Hospitals (2024)
5. Machado, G. G. — HALE: Harmonic Addressing & Labeling Equation (Hubstry, 2025)

---

*Hubstry Deep Tech — HSL Research Module*