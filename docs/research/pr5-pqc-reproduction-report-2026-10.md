# Relatório de reprodução — PR #5 (provedor PQC) sobre a `main` atual

**Data:** 2026-10-05
**Executor:** Claude (agente), reprodução independente.
**Branch:** `feat/pr2-pqc-provider`, atualizada com merge da `main` em `e0055b6` (sem reescrita de histórico).
**Escopo:** atualização do PR #5, reprodução dos 19 testes, suíte integrada, verificação de integridade sintática do repositório e requalificação de `post-quantum/README.md` (item C34 da auditoria).

> **EN summary.** PR #5 was brought up to date with `main` (`e0055b6`) by a merge commit; no PR #5 file changed. Against liboqs 0.16.0 built from source, the 19 PQC tests pass (19/19), and the full tree passes 192 tests across four suites. A repository-wide syntax check, first reported by a separate reviewer and reproduced here, finds one pre-existing error outside this PR's scope (`post-quantum/rho3_bound.py:355`); it is recorded, not fixed. The PQC provider remains unintegrated into `main` until this PR is approved and merged.

---

## 1. Ambiente

| Item | Valor |
|---|---|
| Sistema | Linux 6.18.44, glibc 2.39, x86_64, 2 núcleos |
| Python / pytest | 3.13.16 / 9.1.1 |
| liboqs | 0.16.0, compilada do código-fonte oficial (tag `0.16.0`, commit `5a1a854b`), Release, biblioteca compartilhada |
| liboqs-python | 0.16.0 |

Nenhuma chave ou material secreto foi registrado.

---

## 2. Atualização do PR #5

| Item | Valor |
|---|---|
| Head anterior | `b0a738b` (base `94414dc`) |
| Operação | merge da `main` (`e0055b6`) na branch do PR, commit `fea85b2` |
| Conflitos | nenhum |
| Arquivos do PR #5 alterados pelo merge | nenhum (os cinco arquivos do PR seguem idênticos) |

---

## 3. Resultados

| Gate | Resultado |
|---|---|
| `pytest tests/pqc -v` (T0–T10) | **19 executados, 19 aprovados** |
| `pytest tests/` na árvore atualizada | **192 executados, 192 aprovados**, em quatro suítes distintas: 19 PQC + 5 regressão v0 + 32 HSL v1 + 136 existentes da trilha quântica |

**Classificação.** Esta é a segunda reprodução independente dos 19 testes PQC (a primeira, no mesmo dia, sobre o head `b0a738b`, está em [`hsl-v1-execution-report-2026-10.md`](hsl-v1-execution-report-2026-10.md)). O resultado histórico anterior, obtido em outro ambiente, permanece como evidência histórica.

### 3.1 Medição de CPU (registro, sem inferência)

Execução de `post-quantum/bench_pqc.py` neste ambiente. Medianas em milissegundos:

| Algoritmo | keygen | encaps / sign | decaps / verify |
|---|---|---|---|
| ML-KEM-768 | 0,019 | 0,019 | 0,021 |
| ML-DSA-65 | 0,059 | 0,139 | 0,056 |
| SLH-DSA-SHA2-128s | 71,2 | 544,7 | 0,63 |

Os tempos dependem do ambiente (2 núcleos, nuvem) e diferem da execução histórica. Não permitem inferência de nível de segurança nem de desempenho em produção. O arquivo de saída do benchmark não foi incluído no repositório.

---

## 4. Integridade sintática do repositório

| Item | Valor |
|---|---|
| Comando | `python3 -m compileall -q quantum hsl post-quantum tests` |
| Resultado | **1 erro**, anterior a este PR e fora do seu escopo |
| Local | `post-quantum/rho3_bound.py`, linha 355: `QuantumState.random_state(8, seed=42, "|psi_r1>")` |
| Erro | `SyntaxError: positional argument follows keyword argument` |
| Blob | `1a58107a94d87ba5e4edf38cd9993353b3822fdf`, idêntico na `main` `e0055b6` |
| Origem do achado | identificado por revisão independente (Luna) e reproduzido nesta execução |

**Por que os testes não detectaram:** nenhuma suíte importa `rho3_bound.py`. Portanto, "todos os testes aprovados" não implica que todos os módulos Python do repositório sejam sintaticamente válidos.

**Tratamento:** não corrigido neste PR. O módulo já está bloqueado desde a auditoria de 2026-10-03. Encaminhado ao PR de CI (achado F-10), que deve incluir `compileall` além de `pytest` como gate automático; a correção do arquivo deve preceder a ativação desse gate.

---

## 5. Documentação

`post-quantum/README.md` (item C34 da auditoria):

- A visão geral deixa de dizer que o módulo "implementa a integração" dos padrões NIST com o HALE; passa a descrever um provedor experimental sobre liboqs, com o HALE apenas como contexto de transcript, coerente com a fronteira G4 já documentada no próprio arquivo.
- A validação anterior passa a ser rotulada como evidência histórica; a reprodução independente é registrada ao lado, com os tempos deste ambiente.
- Nota sobre o nome `SLH_DSA_PURE_SHA2_128S` na liboqs 0.16.0.
- Nota de que o HSL v1 não usa este provedor e de que a integração de ML-DSA ao HSL (F-01) é trabalho futuro.
- O exemplo legado `examples/hale_mlkem.py` é marcado como ausente do repositório.

---

## 6. Distinções preservadas

**Cobertura por algoritmo** (ver tabela em `post-quantum/README.md`): ML-KEM-768 e ML-DSA-65 são exercitados em roundtrip, casos negativos, tamanhos e nível de protocolo. SLH-DSA-SHA2-128s é exercitado em disponibilidade, roundtrip e assinatura adulterada (T0, T2, T7); tamanhos, negativos de mensagem e chave trocada e nível de protocolo não são cobertos para ele.

**F-01:** o provedor ML-DSA-65 (parte a) passa a valer na `main` com o merge deste PR; a integração de ML-DSA ao handshake HSL v1 (parte b) continua pendente.

**Gate final do PR #5:**

| Item | Situação |
|---|---|
| 19/19 PQC | Aprovado |
| 192 testes na árvore integrada | Aprovado |
| `compileall` | 1 erro conhecido (F-11), fora do escopo; não bloqueia este PR, bloquearia apenas uma declaração de validade do repositório inteiro |
| README requalificado | Aprovado |
| Escopo do PR | Aprovado |
| Revisão Luna | Pendente |
| Aprovação PI | Pendente |

| Afirmação | Situação |
|---|---|
| Provedor PQC reproduzido de forma independente | Sim (19/19, duas vezes) |
| Provedor PQC integrado à `main` | Não, até a aprovação e o merge deste PR |
| Implementação criptograficamente validada | Não (declarado no próprio README) |
| HSL v1 pós-quântico | Não |

---

## 7. Próximos passos sugeridos

1. Revisão criptográfica e arquitetural deste PR (Luna).
2. Decisão de merge (PI).
3. PR de CI (F-10): gate automático com `pytest` e `compileall`, precedido da correção de `rho3_bound.py:355`.
4. Especificação da integração de ML-DSA ao HSL (F-01), em ciclo próprio.
