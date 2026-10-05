# Auditoria documental do HSL — outubro de 2026

**Status:** diagnóstico (Commit 1 de 2). Nenhum documento existente foi alterado neste commit.
**Snapshot auditado:** `main` em `94414dc` (2026-10-02). Cópia de segurança: branch `backup/main-pre-docs-audit-2026-10-05`.
**Data:** 2026-10-05.
**Natureza do trabalho:** alinhamento entre documentação e implementação. **Não é uma auditoria de segurança** do HSL nem do projeto.

> **EN summary.** This report maps every HSL-related performance and security claim in the repository documentation against the code on `main` at `94414dc`. Each claim is classified, not deleted. The headline results: the ~200-byte handshake is a historical design target (the reference simulation serializes 249 bytes); the ML-DSA-65 signature in the HSL flow is a 64-byte SHA-512 placeholder; `main` contains no PQC implementation (the real provider is in draft PR #5); and the current HSL construction does not provide secret-based cryptographic authentication when `f0` takes its documented default value. Documentation fixes follow in Commit 2, after review by the PI.

---

## 1. Regra de tratamento

Nenhuma afirmação é eliminada só porque não está implementada. Cada uma é **classificada** e recebe um tratamento proporcional à evidência. Metas de projeto continuam no repositório como metas, identificadas como tais. Afirmações de segurança sem demonstração saem do texto descritivo.

### Status

| Status | Significado |
|---|---|
| **Observado** | Confirmado no código ou por execução neste snapshot. |
| **Meta de projeto** | Objetivo declarado; não é resultado e precisa estar rotulado assim. |
| **Não demonstrado** | Não há código, teste ou medição que sustente a afirmação. |
| **Contradito** | O código ou o próprio registro do repositório mostra o contrário. |
| **Não auditado** | Fora do que foi verificado nesta rodada. |
| **Sem evidência** | Afirmação factual sobre atividade externa (comercial, institucional) sem documentação que a sustente. Não é tratada como meta nem hipótese: é removida ou reescrita como intenção futura. |

### Natureza da afirmação

`HIS` histórico/meta · `ARQ` arquitetura · `IMP` implementação · `SEG` segurança · `ROA` roadmap · `COM` comercial

### Regra para afirmações comerciais

Nenhuma empresa é apresentada como prospect, parceira, cliente, piloto ou negociação sem evidência correspondente. As categorias abaixo são distintas e não podem ser misturadas em documento público:

| Categoria | Evidência mínima |
|---|---|
| Alvo (setor ou empresa de interesse) | Nenhuma; deve ser redigido como intenção e, de preferência, por setor |
| Contatada | Registro de contato iniciado |
| Em negociação | Troca documentada de proposta ou termos |
| Parceira | Instrumento firmado (acordo, memorando, carta de intenção) |
| Cliente | Contrato ou pedido |
| Piloto | Instrumento de piloto e escopo acordado |

O histórico do Git é público e permanente; uma afirmação desse tipo deixa registro verificável mesmo depois de corrigida.

---

## 2. Método

1. Leitura de `hsl/hsl_module.py` (único módulo de handshake do HSL na `main`) e inventário de `post-quantum/`.
2. Execução da simulação de referência incluída no próprio módulo (`python3 hsl/hsl_module.py`) e de um teste mínimo de aceitação (seção 6).
3. Busca sistemática de afirmações em 11 arquivos `.md`: `README.md`, `hsl/README.md`, `docs/architecture.md`, `docs/security-architecture.md`, `roadmap/2025-2026.md`, `roadmap/2026-2027.md`, `attack-vectors/README.md`, `compliance/README.md`, `SECURITY.md`, `post-quantum/README.md`, `quantum/README.md`.
4. Varredura de nomes de empresas e de termos comerciais (parceiro, cliente, piloto, negociação, carta de intenção) em todos os arquivos `.md`.
5. Os números de linha referem-se ao snapshot `94414dc`.

**Limites do método.** `hsl/intrusion_detection.py` e `hsl/lfsr_key_rotation.py` não foram auditados nesta rodada. Não houve revisão criptográfica formal; os achados da seção 5 descrevem o comportamento observável do código.

---

## 3. Resumo

| Tema | Resultado |
|---|---|
| Tamanho do handshake (~200 B) | Meta histórica. A simulação de referência serializa **249 B** (57 + 79 + 113), com identificadores de 13 e 11 caracteres. |
| Comparação com TLS 1.3 (~8 KB, 97,5%) | Não demonstrada. Não há benchmark (medição comparativa) no repositório; as duas construções pertencem a categorias diferentes (seção 4.2, C15). |
| ML-DSA-65 no HSL | Contradito. A etapa 3 usa um placeholder: `SHA-512(token ‖ f0)` truncado em 64 B (`hsl_module.py:411`). |
| PQC na `main` | Contradito. A `main` não contém implementação de ML-KEM, ML-DSA ou SLH-DSA; o provedor real está no PR #5 (rascunho). |
| HALE como derivação de chaves | Não demonstrado. Não há hierarquia de chaves implementada na `main`; o exemplo do README devolve o mesmo valor em todos os níveis (C05). |
| Autenticação do HSL | A construção atual não fornece autenticação criptográfica baseada em segredo quando `f0` assume o valor padrão documentado (F-03). |
| Afirmações comerciais | Uma única menção nominal a empresas (C33: Claro, TIM, Vivo) e uma menção genérica a funil de parceiros (C36), ambas sem evidência. As demais referências a "parceiro telecom" ou "piloto" aparecem como entregas futuras de roadmap e estão corretas como metas. |
| Disciplina de pesquisa | `quantum/README.md` e a seção "Current Research Status" do README já seguem o padrão correto de não reivindicação; servem de modelo para a requalificação. |

---

## 4. Inventário de afirmações

### 4.1 `README.md`

| ID | Linha | Afirmação | Natureza | Evidência | Status | Tratamento proposto |
|---|---|---|---|---|---|---|
| C01 | 62, 70 | Handshake de ~200 B contra ~8 KB do TLS 1.3, "mantendo resistência computacional equivalente", "ideal para IoT, telecomunicações" | HIS · SEG | Simulação: 249 B. Assinatura simulada. Sem benchmark nem análise de segurança. | Contradito (tamanho) · Não demonstrado (equivalência, adequação) | Reescrever: meta histórica de ~200 B, não validada; placeholder declarado; remover a equivalência; "aplicações-alvo em investigação". |
| C02 | 21, 108 | "HSL Auth … (~200B)"; diagrama "Autenticação harmônica ~200B" | HIS | Idem C01 | Contradito | "meta histórica ~200 B, não validada" / "Autenticação harmônica (hipótese)". |
| C03 | 10 | Selo "PQC Ready — NIST FIPS 203/204/205" | IMP | Nenhum `import oqs` ou implementação PQC na `main`; `post-quantum/` contém apenas `profile_lattice.py`, `quantum_profiles.py`, `rho3_bound.py`. | Contradito (na `main`) | Selo "PQC experimental". |
| C04 | 60, 68 | HALE "deriva hierarquias de chaves … oferecendo separabilidade espectral natural para … autenticação leve" | ARQ · SEG | Sem hierarquia de chaves implementada na `main`. | Não demonstrado | HALE como framework de pesquisa que originou a investigação; propriedades criptográficas em investigação. |
| C05 | 142–152 | Exemplo "ML-KEM-768 com HALE" | IMP | Não usa ML-KEM. Calcula `fk` e o descarta; devolve `sha256(str(f0))`, idêntico para qualquer `level` e `b`. | Contradito | Rotular como ilustrativo e não funcional, ou retirar o título "ML-KEM-768". |
| C06 | 133 | Pré-requisito "liboqs 0.10+" | IMP | A `main` não usa liboqs; o PR #5 usa 0.16.0. | Não aplicável à `main` | Manter até a integração do PR #5; anotar dependência. |
| C07 | 158–164 | Roadmap: Fase 1 Q2 2026 (benchmarks contra TLS 1.3), Fase 2 Q3 2026 | ROA | Prazos vencidos sem benchmark registrado. | Meta de projeto (vencida) | Marcar como "replanejado". Novas datas a definir pelo PI. |

### 4.2 `hsl/README.md`

| ID | Linha | Afirmação | Natureza | Evidência | Status | Tratamento proposto |
|---|---|---|---|---|---|---|
| C08 | 9, 11 | ~200 B; "redução de 97,5%" em relação ao TLS 1.3 | HIS | Idem C01 | Contradito (tamanho) · Não demonstrado (redução) | Meta histórica; remover o percentual. |
| C09 | 15–40 | Diagrama: CHALLENGE 48 B `[fA, nonceA, timestamp]`, RESPONSE 48 B `[fB, nonceB, gcd(fA,fB) sig]`, VERIFY 104 B `[HSL_token, PQC_sign, session_id]` | IMP | Código: 44 B + `node_id`; 68 B + `node_id` com `sigma` SHA-256 (não `gcd`); 113 B. | Contradito | Atualizar campos e tamanhos para o código, ou rotular como desenho histórico. |
| C10 | 48, 64 | "Resistência quântica: composto com ML-DSA-65"; "Native (ML-DSA-65)" | SEG | Placeholder SHA-512 (F-01). | Contradito | "Planejado: integração ML-DSA-65; atualmente placeholder." |
| C11 | 50 | Forward secrecy por "frequências harmônicas derivadas por sessão (ephemeral)" | SEG | A fase é determinística: `sha256(node_id) mod 12` (`hsl_module.py:269`); não há troca de chaves efêmeras. | Contradito | Retirar como propriedade; registrar como objetivo de pesquisa. |
| C12 | 51 | Autenticação mútua: "ambos os nós provam conhecimento de f0" | SEG | Só o respondente produz prova (`sigma`). Não há verificação da etapa 3 pelo respondente (F-05). | Contradito | "Autenticação unilateral na implementação atual; mútua planejada." |
| C13 | 52 | Personificação exigiria "resolver discrete log no espaço harmônico" | SEG | Problema não definido; aceitação depende apenas de `f0` (F-03). | Não demonstrado | Retirar como propriedade. |
| C14 | 49, 53 | Proteção contra replay (nonce + timestamp, 60 s); liveness | SEG | Janela de tempo verificada (`hsl_module.py:350`); não há registro de nonces já vistos (F-08). | Observado (parcial) | "Janela temporal implementada; registro de nonces pendente." |
| C15 | 61–68 | Tabela HSL × TLS: RTT, CPU ~0,3 ms, memória ~2 KB, certificado 0 B | HIS · SEG | Sem medição. A própria seção de limitações (linha 141) já declara CPU e memória "estimados". Certificado 0 B decorre de segredo pré-compartilhado (`f0`); o TLS 1.3 autentica partes sem segredo prévio. | Não demonstrado · Categoria distinta | Marcar valores como "não medidos"; nota sobre a diferença de categoria. |
| C16 | 70 | "Otimizado para … IoT, telecomunicações, sistemas embarcados" | HIS | Sem teste em ambiente-alvo. | Não demonstrado | "Aplicações-alvo em investigação." |
| C17 | 76–132 | Implementação de referência em `reference-impl/hsl_handshake.py` | IMP | Arquivo inexistente. O trecho não importa `hashlib`, concatena `bytes` e `str` (erro de tipo), devolve `"authenticated": True` incondicionalmente e grava `"total_bytes": 200` como constante. | Contradito | Rotular como pseudocódigo histórico; apontar para `hsl/hsl_module.py`. |
| C18 | 139 | "Em modo híbrido (HSL + PQC), a proteção MITM é completa" | SEG | Modo híbrido inexistente na `main`. MITM (Man-in-the-Middle): ataque de intermediário. | Não demonstrado | Retirar "completa"; "objetivo do modo híbrido". |

### 4.3 `docs/architecture.md`

| ID | Linha | Afirmação | Natureza | Evidência | Status | Tratamento proposto |
|---|---|---|---|---|---|---|
| C19 | 13, 25, 52 | Handshake de ~200 B contra ~8 KB; "Token (~200B)" | HIS | Idem C01 | Contradito | Idem C01. |
| C20 | 5, 9, 11, 48, 50 | HALE Core deriva endereços, chaves criptográficas e tokens; PQC Module implementa FIPS 203/204/205 integrado ao HALE | ARQ · IMP | Sem hierarquia de chaves nem PQC na `main`. | Não demonstrado · Contradito (PQC) | Descrever como arquitetura-alvo; PQC "em desenvolvimento (PR #5)". |
| C21 | 64–66 | TRL 4 em Q2 2026, TRL 5 em Q3 2026 com parceiro telecom | ROA | Prazos vencidos. TRL: Technology Readiness Level, escala de maturidade de 1 a 9. | Meta de projeto (vencida) | "Replanejado". |

### 4.4 `docs/security-architecture.md`

| ID | Linha | Afirmação | Natureza | Evidência | Status | Tratamento proposto |
|---|---|---|---|---|---|---|
| C22 | 60–70, 209 | Tabela 48 + 48 + 104 = ~200 B; parâmetro "HSL handshake ~200 bytes" | HIS · IMP | Idem C09 | Contradito | Atualizar para o código ou rotular como desenho histórico. |
| C23 | 74–76 | Prova mútua de `f0`; "Quantum resistance: composable with ML-DSA-65"; forward secrecy | SEG | Idem C10–C12 | Contradito · Não demonstrado | Idem C10–C12. |
| C24 | 166–185 | Fluxo e modelo de ameaças apoiados em "rho_3 bound" contra força bruta quântica e MITM | SEG | O README registra `rho3_bound.py` como "experimentalmente inválido e cientificamente bloqueado" (auditoria de 2026-10-03). | Contradito (pelo registro do repositório) | Anotar o bloqueio do ρ₃ nas linhas que dependem dele. |
| C25 | 101, 106 | Semente LFSR = `SHA-256(f0 ‖ timestamp_ns)`; "f0 (shared secret)" | SEG | `lfsr_key_rotation.py` fora desta rodada. | Não auditado | Avaliar em rodada própria. |

### 4.5 Demais arquivos

| ID | Arquivo:linha | Afirmação | Natureza | Evidência | Status | Tratamento proposto |
|---|---|---|---|---|---|---|
| C26 | `attack-vectors/README.md:24, 38` | Mitigações por ML-KEM-768 + ML-DSA-65 e "HSL + ML-DSA-65 mutual authentication" | SEG | Sem PQC na `main`; HSL sem autenticação mútua. | Contradito | "Mitigação planejada". |
| C27 | `attack-vectors/README.md:98, 134` | HSL "elimina necessidade de credenciais tradicionais"; "verificação de identidade independente de DNS" | SEG | Sem demonstração. | Não demonstrado | "Hipótese de mitigação". |
| C28 | `compliance/README.md:27, 29, 49` | Mapeamentos NIS2 e NIST CSF a "PQC Module (ML-KEM-768 + AES-256-GCM)" e "HSL coherence token + ML-DSA-65" | SEG | Controles não implementados na `main`. NIS2: diretiva europeia de segurança de redes. NIST CSF: Cybersecurity Framework. | Contradito | Rotular como "controle planejado". |
| C29 | `SECURITY.md:44–45` | ML-KEM "integração em progresso"; ML-DSA "planejado para Q3 2026" | ROA | Coerente com o PR #5 em rascunho; data de Q3 vencida. | Observado · Meta vencida | Referenciar o PR #5. |
| C30 | `roadmap/2025-2026.md:50–52` | F0-04 a F0-06 "Done", incluindo o limite ρ₃ | ROA | ρ₃ bloqueado (ver C24). | Contradito (pelo registro do repositório) | Anotar "bloqueado em 2026-10-03". |
| C31 | `roadmap/2025-2026.md:84–85` | "Current Target": ~200 B, ~0,3 ms P99 | HIS | Rotulado como meta. | Meta de projeto | Manter; acrescentar "não medido". |
| C32 | `roadmap/2026-2027.md:30, 40, 43` | Benchmark HSL × TLS 1.3 (jun/2026) e paper HALE em conferência (jul/2026) | ROA | Não há relatório de benchmark no repositório. | Meta de projeto (vencida) | "Replanejado". |
| C33 | `roadmap/2026-2027.md:104` | "Múltiplos parceiros prospectados (Claro, TIM, Vivo)", como mitigação de risco | COM | Nenhuma evidência documental de contato foi fornecida; o PI confirmou em 2026-10-05 que os nomes devem sair. | Sem evidência | Remover os três nomes. Reescrever como intenção futura, sem sugerir atividade comercial ocorrida. |
| C36 | `roadmap/2025-2026.md:176` | Mitigação "Multiple partner pipeline" | COM | Pressupõe um funil de parceiros existente; nenhuma evidência fornecida. | Sem evidência | Reescrever como intenção futura ("prospecção de múltiplos parceiros prevista"). |
| C34 | `post-quantum/README.md:25, 35, 49–60, 84` | Hierarquia de chaves HALE; assinatura "HALE-PQ" com ML-DSA-65; `examples/hale_mlkem.py` | ARQ · IMP | Diretório `examples/` inexistente; sem implementação na `main`. | Contradito · Não demonstrado | **Não editar neste PR.** O arquivo também é alterado pelo PR #5; a requalificação acontece na revisão do PR #5. |
| C35 | `quantum/README.md:3–5, 99, 110` | Não reivindica segurança quântica, vantagem quântica nem nível criptográfico | — | Coerente com o código. | Observado | Manter. Modelo de redação para os demais. |

---

## 5. Achados de implementação (fora do escopo deste PR)

Registrados para trabalho de engenharia posterior. Nenhum é corrigido neste PR.

| ID | Prioridade | Achado | Local |
|---|---|---|---|
| F-01 | Alta | A "assinatura PQC" da etapa 3 é `SHA-512(token_ab ‖ str(f0))` truncado em 64 B. Não envolve chave privada nem algoritmo de assinatura. O próprio código a declara placeholder. | `hsl_module.py:169, 410–411` |
| F-02 | Alta | A docstring de `_compute_coherence_signature` declara "HMAC-SHA256"; a implementação usa SHA-256 sem chave. HMAC (Hash-based Message Authentication Code) exige chave secreta. O mesmo vale para `token_ab`, descrito como "HMAC-based". | `hsl_module.py:168, 293, 302` |
| F-03 | Alta | **A construção atual não fornece autenticação criptográfica baseada em segredo quando `f0` assume o valor padrão documentado.** Entradas de `sigma`: `phase_a` e `phase_b` (transmitidas em claro), `nonce_a` e `nonce_b` (transmitidos em claro) e `f0` (configuração; padrão `440.0`, publicado na documentação). Verificação: um nó com identificador arbitrário, nunca registrado, e configuração padrão é aceito (`authenticated=True`); com `f0=441.0`, é rejeitado (seção 6). A aceitação depende exclusivamente de `f0`. Mesmo quando não público, `f0` é um número real escolhido por pessoa, não uma chave gerada com entropia controlada. | `hsl_module.py:201, 273–302, 375–400` |
| F-04 | Média | A fase do par não é conferida contra o registro: `verify_peer_phase` existe, mas não é chamada no handshake. A fase deriva do hash do `node_id` público, com 12 valores possíveis. | `hsl_module.py:269, 424–434` |
| F-05 | Média | Não há verificação da etapa 3 pelo respondente: nenhum método valida `HVerify`. A autenticação implementada é unilateral. | `hsl_module.py` (ausência) |
| F-06 | Média | Serialização sem delimitação: `node_id`, de tamanho variável, é concatenado sem prefixo de comprimento; não há `from_bytes` para as mensagens. A mensagem não é decodificável de forma inequívoca. | `hsl_module.py:96–104, 140–148` |
| F-07 | Média | O resultado local `authenticated` é serializado e enviado ao par (`struct.pack(">?")`). O receptor não deve confiar nesse campo. | `hsl_module.py:179–186` |
| F-08 | Baixa | Não há registro de nonces já utilizados; uma mensagem pode ser reapresentada dentro da janela de 60 s. | `hsl_module.py:106–109, 350` |
| F-09 | Média | Não há testes automatizados do HSL: `tests/` cobre apenas encoding e lattice64. | `tests/` |
| F-10 | Informativo | O repositório não possui CI (integração contínua) em `.github/workflows`. Mudanças documentais não acionam verificações automáticas; links internos devem ser conferidos manualmente na revisão. | raiz |

---

## 6. Reprodução

```bash
git checkout 94414dc
python3 hsl/hsl_module.py
# saída: "Total bytes exchanged: ~249"

python3 - <<'EOF'
import sys; sys.path.insert(0, "hsl")
from hsl_module import HSLEngine, HSLEngineConfig
a = HSLEngine("alice-node-01"); b = HSLEngine("bob-node-02")
c = a.create_challenge(); r = b.process_challenge(c); v = a.verify_response(c, r)
print(len(c.to_bytes()), len(r.to_bytes()), len(v.to_bytes()))      # 57 79 113
m = HSLEngine("mallory")                                              # nunca registrado
print(a.verify_response(c, m.process_challenge(c)).authenticated)     # True
m2 = HSLEngine("mallory", HSLEngineConfig(f0=441.0))
print(a.verify_response(c, m2.process_challenge(c)).authenticated)    # False
EOF
```

---

## 7. Próximo passo (Commit 2, após revisão do PI)

Requalificação documental conforme a coluna "Tratamento proposto", em 10 arquivos:
`README.md`, `hsl/README.md`, `docs/architecture.md`, `docs/security-architecture.md`, `roadmap/2025-2026.md`, `roadmap/2026-2027.md`, `attack-vectors/README.md`, `compliance/README.md`, `SECURITY.md` e, apenas se necessário, `quantum/README.md`.

Fora do Commit 2: `post-quantum/README.md` (PR #5), qualquer arquivo `.py`, e os achados F-01 a F-10.

**Decidido pelo PI (2026-10-05):** remoção dos nomes de empresas em C33, aplicada no Commit 2.

**Decisões pendentes do PI:** novas datas do roadmap (C07, C21, C32); redação de substituição em C33 e C36.
