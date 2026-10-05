# Relatório de execução — HSL Auth v1 e reprodução PQC

**Data:** 2026-10-05
**Executor:** Claude (agente), reprodução independente.
**Branch:** `fix/hsl-auth-v1` a partir da `main` em `aa242a1`.
**Escopo:** achados F-02 a F-09 da [auditoria documental](hsl-documentation-audit-2026-10.md). F-01 e F-10 permanecem abertos.

> **EN summary.** Independent reproduction of the 19 PQC tests of PR #5 (19/19 PASS against liboqs 0.16.0 built from source), implementation of HSL Auth v1 (PSK + HMAC-SHA-256), and a combined run of PR #5 with HSL v1 (192/192 PASS, including the 19 PQC tests). The earlier 19/19 result remains historical evidence from a different environment; this run is a separate reproduction. No secret material is recorded here.

---

## 1. Ambiente

| Item | Valor |
|---|---|
| Sistema | Linux 6.18.44, glibc 2.39 |
| Arquitetura | x86_64 |
| Python | 3.13.16 |
| pytest | 9.1.1 |
| liboqs | 0.16.0, compilada a partir do código-fonte oficial (`open-quantum-safe/liboqs`, tag `0.16.0`, commit `5a1a854b`), build Release, biblioteca compartilhada |
| liboqs-python | 0.16.0 |
| Início da execução (UTC) | 2026-10-05T17:40:22Z |

Nenhuma chave, PSK ou material secreto foi registrado.

---

## 2. Reprodução da linha de base PQC (PR #5)

| Item | Valor |
|---|---|
| Código | branch `feat/pr2-pqc-provider`, head `b0a738b` |
| Comando | `pytest tests/pqc -v` |
| Resultado | **19 passed, 0 failed, 0 skipped** |

Testes: T0 (proveniência), T1 (KEM roundtrip), T2 (assinatura ML-DSA-65 e SLH-DSA), T3 (assinatura negativa), T4 (KEM negativo em nível de protocolo), T5 (tamanhos), T6 (registro), T7 (agilidade), T8 (registro de ambiente), T9a–T9e (transcript canônico), T10 (HKDF: vetor RFC 5869, separação de domínio, vinculação ao transcript, codificação injetiva).

**Classificação.** O resultado 19/19 anterior, obtido em outro ambiente, permanece como evidência histórica. Esta execução é uma **reprodução independente**, em ambiente distinto, sobre o mesmo commit.

**Observação sobre SLH-DSA.** A liboqs 0.16.0 registra o algoritmo como `SLH_DSA_PURE_SHA2_128S`. O identificador `SLH-DSA-SHA2-128s` não aparece na lista de mecanismos da biblioteca; o adaptador do PR #5 (`post-quantum/oqs_adapter.py`) faz a tradução. Uma verificação manual com o nome do padrão retorna "indisponível" mesmo quando o algoritmo está habilitado.

---

## 3. HSL Auth v1

### 3.1 Suítes

| Suíte | Resultado |
|---|---|
| `tests/test_hsl_v0_regression.py` (achados reproduzidos na v0) | 5 passed |
| `tests/test_hsl_auth_v1.py` | 32 passed |
| Suíte completa da `main` + HSL v1 | 173 passed |

Os testes de regressão da v0 **passam quando a fragilidade conhecida é reproduzida**: em particular, um nó nunca registrado, com o f0 padrão, é aceito pela v0 (F-03).

### 3.2 Correspondência com os achados

| Achado | Teste(s) na v1 | Resultado |
|---|---|---|
| F-02 HMAC declarado, não usado | `test_f02_response_tag_is_hmac_over_transcript` | Corrigido |
| F-03 aceitação dependente só de f0 | `test_f03_attacker_knowing_f0_but_not_key_is_rejected`, `test_f03_attacker_cannot_complete_as_initiator_without_key`, `test_wrong_context_f0_is_rejected` | Corrigido |
| F-04 fase do par não conferida | `test_f04_inconsistent_phase_slot_is_rejected`, `test_f04_peer_registry_is_enforced` | Corrigido (verificação de contexto, não de autenticação) |
| F-05 etapa 3 não verificada | `test_f05_tampered_verify_is_rejected`, `test_f03_attacker_cannot_complete_as_initiator_without_key` | Corrigido |
| F-06 mensagens sem delimitação | `test_f06_roundtrip_preserves_all_fields`, `test_f06_truncated_and_trailing_bytes_are_rejected`, `test_f06_wrong_message_type_is_rejected` | Corrigido |
| F-07 flag de autenticação na mensagem | `test_f07_no_authentication_flag_on_the_wire` | Corrigido |
| F-08 sem registro de nonces | `test_f08_replayed_challenge_is_rejected`, `test_f08_replayed_verify_is_rejected`, `test_replayed_response_is_rejected`, `test_stale_challenge_is_rejected`, `test_expired_pending_challenge_is_rejected` | Corrigido, com a limitação da seção 4 |
| F-09 sem testes do HSL | As duas suítes acima | Corrigido |

Também cobertos: reflexão da própria mensagem, resposta de par inesperado, uso de uma tag de uma direção na outra, adulteração de campos, PSK curta e ausência de segredos no `repr`.

### 3.3 Verificação dos testes por mutação

Para confirmar que os testes detectam falhas reais, cinco defeitos foram introduzidos temporariamente na implementação, um de cada vez, e a suíte foi executada. Todos foram detectados:

| Defeito introduzido | Testes que falharam |
|---|---|
| Iniciador deixa de verificar a tag da resposta | 5 |
| Respondente deixa de verificar a etapa 3 | 3 |
| Rótulos de direção iguais | 1 |
| Registro de nonces desativado | 1 |
| HMAC substituído por SHA-256 sem chave | 2 |

A implementação foi restaurada antes do commit.

### 3.4 Tamanhos medidos

Medição da simulação `python3 hsl/hsl_auth_v1.py`, com identificadores de 13 e 11 bytes:

| Mensagem | Bytes |
|---|---|
| Challenge | 58 |
| Response | 112 |
| Verify | 66 |
| **Total** | **236** |

O tamanho depende do comprimento dos identificadores. Esta é uma medição da implementação experimental, não um benchmark, e não foi comparada com o TLS 1.3. A v1 não inclui assinatura pós-quântica; a integração de ML-DSA (F-01) alteraria esses valores.

---

## 4. Limitações declaradas da v1

- A PSK é distribuída fora do protocolo; a distribuição de chaves não faz parte deste trabalho.
- A detecção de replay vale durante a vida de uma instância do motor, dentro da janela de tempo configurada. Não sobrevive a reinício do processo nem é compartilhada entre instâncias.
- Não há sigilo futuro (*forward secrecy*): o comprometimento da PSK afeta as sessões passadas e futuras com aquela chave.
- Não há assinatura pós-quântica (F-01, dependente do PR #5).
- Uma resposta inválida consome o desafio pendente correspondente; o iniciador precisa iniciar um novo handshake.
- Nenhuma revisão criptográfica externa foi realizada.

---

## 5. Execução combinada (PR #5 + HSL v1)

| Item | Valor |
|---|---|
| Base | `feat/pr2-pqc-provider` (`b0a738b`) com merge local de `fix/hsl-auth-v1` (`e8f15f5`); não enviado ao repositório |
| Comando | `pytest tests/ -v` |
| Resultado | **192 passed** (19 PQC + 5 regressão v0 + 32 HSL v1 + 136 da trilha quântica) |

O HSL v1 não altera nenhum arquivo do PR #5; os dois conjuntos de mudanças não se sobrepõem.

---

## 6. Reprodução

```bash
# liboqs 0.16.0
git clone --depth 1 --branch 0.16.0 https://github.com/open-quantum-safe/liboqs.git
cmake -S liboqs -B liboqs/build -GNinja -DBUILD_SHARED_LIBS=ON -DOQS_BUILD_ONLY_LIB=ON \
      -DCMAKE_INSTALL_PREFIX=$PWD/oqs-install -DCMAKE_BUILD_TYPE=Release
ninja -C liboqs/build install
python3 -m venv .venv && . .venv/bin/activate
pip install liboqs-python==0.16.0 pytest numpy
export OQS_INSTALL_PATH=$PWD/oqs-install LD_LIBRARY_PATH=$PWD/oqs-install/lib

# Linha de base PQC
git checkout b0a738b && pytest tests/pqc -v

# HSL v1
git checkout fix/hsl-auth-v1 && pytest tests/ -v
python3 hsl/hsl_auth_v1.py
```

A compilação da liboqs levou cerca de 7 minutos neste ambiente (vários núcleos, sem limite apertado de memória). Em máquinas com 8 GB de RAM, recomenda-se executar em ambiente de nuvem ou em CI.
