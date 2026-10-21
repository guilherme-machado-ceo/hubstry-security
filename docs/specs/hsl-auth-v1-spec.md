# Especificação formal — HSL Auth v1 (PSK-HMAC)

| Item | Valor |
|---|---|
| Documento | Especificação técnica normativa do protocolo de autenticação HSL Auth v1 |
| Versão do documento | 0.1 (rascunho para revisão) |
| Implementação de referência | [`hsl/hsl_auth_v1.py`](../../hsl/hsl_auth_v1.py), última alteração no commit `e8f15f5`; `main` em `656c6b8` |
| Estado | Protocolo experimental. Sem revisão criptográfica externa. Verificação formal simbólica do modelo documentada na seção 12; não há verificação formal do código Python nem prova computacional. |

As palavras **DEVE**, **NÃO DEVE** e **PODE** têm sentido normativo, no estilo da RFC 2119 (convenção da IETF — Internet Engineering Task Force — para requisitos em especificações).

---

## 1. Objetivo e escopo

O HSL Auth v1 é um protocolo de **autenticação mútua** entre dois nós que compartilham uma chave secreta prévia (PSK, *Pre-Shared Key*). Em três mensagens, cada nó obtém evidência de que o outro conhece a PSK e participou da mesma execução do protocolo, com os mesmos identificadores, nonces e contexto.

**Propriedades pretendidas:** sob as premissas da seção 4, o protocolo visa às propriedades P1 a P4 da seção 9. A evidência formal disponível vale para o modelo simbólico e para as abstrações descritas na seção 12; não constitui verificação do código nem prova computacional (seção 12.5).

**O protocolo não estabelece chave de sessão.** O valor `session_id` produzido ao final é um identificador local de correlação. Nesta versão ele não é designado como chave criptográfica e NÃO DEVE ser usado para cifrar ou autenticar dados da aplicação (ver seção 10, item H-3).

**Papel do contexto harmônico.** A frequência fundamental `f0`, a base `base` e a fase harmônica de cada nó (`slot`) são parâmetros públicos de contexto e identificação. Entram no transcript autenticado, mas não são segredos e não contribuem para a segurança. **Toda a segurança do protocolo deriva da PSK e do HMAC-SHA-256.**

---

## 2. Notação e primitivas

| Símbolo | Significado |
|---|---|
| `‖` | Concatenação de sequências de bytes |
| `lp(x)` | Campo prefixado pelo comprimento: `u32_be(len(x)) ‖ x` |
| `u8`, `u16_be`, `u32_be`, `u64_be` | Inteiro sem sinal de 1, 2, 4 ou 8 bytes; `_be` = big-endian |
| `f64_be(x)` | Número em ponto flutuante IEEE 754 de 64 bits, big-endian |
| `MAC(K, x)` | HMAC-SHA-256 (RFC 2104 e FIPS 198-1) com chave `K` sobre `x`; saída de 32 bytes |
| `Rand(n)` | `n` bytes de um gerador criptograficamente seguro |
| `slot(id)` | `int_be(SHA-256(utf8(id))) mod base` — computável por qualquer um |
| `K` | PSK do par de nós |
| `W` | Janela temporal em segundos (padrão: 60) |

**Constantes**

| Nome | Valor |
|---|---|
| `PROTOCOL_ID` | `"HSL-v1"` (ASCII) |
| `VERSION` | `1` |
| `MSG_CHALLENGE`, `MSG_RESPONSE`, `MSG_VERIFY` | `1`, `2`, `3` |
| `L_RESP` | `"HSL-v1/response"` |
| `L_VER` | `"HSL-v1/verify"` |
| `L_SESS` | `"HSL-v1/session"` |
| `NONCE_LEN`, `TAG_LEN` | 32 bytes |
| `SESSION_ID_LEN` | 16 bytes |
| `MIN_PSK_LEN` | 32 bytes |
| Identificador de nó | 1 a 255 bytes em UTF-8 |

Os três rótulos diferem já no oitavo byte (`r`, `v`, `s`), e nenhum é prefixo de outro. Assim, as entradas do HMAC nos três usos nunca coincidem, o que garante separação de domínio entre os usos da mesma chave.

---

## 3. Participantes e papéis

- **Iniciador (A):** envia a mensagem 1 e a mensagem 3.
- **Respondente (B):** envia a mensagem 2.

Um mesmo nó PODE atuar nos dois papéis, em execuções distintas.

---

## 4. Premissas de implantação (normativas)

| ID | Premissa |
|---|---|
| A1 | `K` é gerada uniformemente ao acaso, com pelo menos 32 bytes, e distribuída fora do protocolo por canal seguro. |
| A2 | **`K` é exclusiva do par de nós (A, B).** Nenhum terceiro nó conhece `K`. Se a mesma PSK for compartilhada por mais de dois nós, as garantias de identidade da seção 9 não valem entre eles (ver H-2). |
| A3 | Os identificadores de nó são únicos no domínio de implantação. |
| A4 | Cada nó mantém os relógios sincronizados com erro inferior a `W`. |
| A5 | `Rand` produz valores imprevisíveis e não repetidos. Com 32 bytes, a probabilidade de colisão é desprezível. |
| A6 | A implementação de HMAC-SHA-256 é correta e as comparações de tags são feitas em tempo constante. |

---

## 5. Diagrama de sequência

```mermaid
sequenceDiagram
    participant A as Iniciador A
    participant B as Respondente B
    Note over A: nA ← Rand(32), tA ← agora<br/>guarda pendente[nA] = (desafio, B)
    A->>B: 1. Challenge(idA, slotA, nA, tA)
    Note over B: verifica par, slotA, |agora − tA| ≤ W,<br/>(idA, nA) não visto<br/>nB ← Rand(32)<br/>T ← transcript(...)<br/>tagB ← MAC(K, L_RESP ‖ T)
    B->>A: 2. Response(idB, slotB, nA, nB, tagB)
    Note over A: localiza pendente[nA], confere idB esperado e slotB<br/>verifica tagB<br/>tagA ← MAC(K, L_VER ‖ T ‖ lp(tagB))<br/>A aceita; sid ← MAC(K, L_SESS ‖ T ‖ lp(tagB))[0..16]
    A->>B: 3. Verify(nB, tagA)
    Note over B: localiza pendente[nB]<br/>verifica tagA<br/>B aceita; sid ← mesmo cálculo
```

---

## 6. Sintaxe

### 6.1 Formato das mensagens

Todas as mensagens começam com o cabeçalho `u8(VERSION) ‖ u8(tipo)`.

**Mensagem 1 — Challenge (A → B)**

| Campo | Codificação | Bytes |
|---|---|---|
| versão | `u8` = 1 | 1 |
| tipo | `u8` = 1 | 1 |
| `len(idA)` | `u8` | 1 |
| `idA` | UTF-8 | 1–255 |
| `slotA` | `u16_be` | 2 |
| `nA` | bytes | 32 |
| `tA` | `u64_be`, segundos Unix | 8 |

**Mensagem 2 — Response (B → A)**

| Campo | Codificação | Bytes |
|---|---|---|
| versão, tipo | `u8` = 1, `u8` = 2 | 2 |
| `len(idB)`, `idB` | `u8`, UTF-8 | 2–256 |
| `slotB` | `u16_be` | 2 |
| `nA` | bytes | 32 |
| `nB` | bytes | 32 |
| `tagB` | bytes | 32 |

**Mensagem 3 — Verify (A → B)**

| Campo | Codificação | Bytes |
|---|---|---|
| versão, tipo | `u8` = 1, `u8` = 3 | 2 |
| `nB` | bytes | 32 |
| `tagA` | bytes | 32 |

Tamanho total medido na implementação de referência, com identificadores de 13 e 11 bytes: 58 + 112 + 66 = 236 bytes.

### 6.2 Regras de decodificação

Um receptor DEVE rejeitar a mensagem quando:
- a versão for diferente de 1 ou o tipo não for o esperado;
- faltarem bytes (mensagem truncada) ou sobrarem bytes após o último campo;
- o identificador tiver comprimento 0 ou não for UTF-8 válido.

Nenhuma mensagem contém indicador de "autenticado": o resultado da autenticação é sempre estado local.

### 6.3 Transcript

```
T = lp(PROTOCOL_ID) ‖ lp(f64_be(f0)) ‖ lp(u16_be(base))
  ‖ lp(utf8(idA)) ‖ lp(u16_be(slotA)) ‖ lp(nA) ‖ lp(u64_be(tA))
  ‖ lp(utf8(idB)) ‖ lp(u16_be(slotB)) ‖ lp(nB)
```

Como todo campo é prefixado pelo comprimento, a codificação é injetiva: dois transcripts diferentes nunca produzem a mesma sequência de bytes.

### 6.4 Valores derivados

```
tagB = MAC(K, L_RESP ‖ T)
U    = T ‖ lp(tagB)
tagA = MAC(K, L_VER  ‖ U)
sid  = MAC(K, L_SESS ‖ U)[0 .. 16)
```

---

## 7. Semântica

### 7.1 Estado de cada nó

| Estrutura | Conteúdo | Validade |
|---|---|---|
| `pend_I[nA]` | `(desafio, par esperado, instante de criação)` | `W` segundos após a criação |
| `pend_R[nB]` | `(U, instante de criação, idA)` | `W` segundos após a criação |
| `seen[(idA, nA)]` | instante de expiração `tA + W` | Até o último instante em que `tA` ainda é aceito pela janela (inclusive) |

Esse estado é volátil: vive enquanto a instância do motor estiver ativa e não é compartilhado entre instâncias. As operações de uma instância são serializadas por uma trava interna, e o estado pendente só é consumido depois que a mensagem passa por todas as verificações.

### 7.2 Máquina de estados por execução

| Papel | Estados |
|---|---|
| Iniciador | `INICIAL → AGUARDA_RESPOSTA → ACEITO`, ou `→ REJEITADO` |
| Respondente | `INICIAL → AGUARDA_VERIFY → ACEITO`, ou `→ REJEITADO` |

Uma execução só chega a `ACEITO` se todas as verificações da seção 8 passarem. Qualquer falha leva a `REJEITADO`, sem mensagem de erro ao par.

### 7.3 Verificação de par (`check_peer`)

Ao processar uma mensagem que traz um identificador de par `id` com fase `s`, o nó DEVE rejeitar quando:
1. `id` for igual ao próprio identificador (proteção contra reflexão);
2. houver registro de pares configurado e `id` não estiver nele;
3. `s ≠ slot(id)`.

Essa verificação é de política e consistência. Ela não autentica ninguém.

---

## 8. Pseudocódigo dos algoritmos locais

```
procedure INITIATE(peer):
    require peer ≠ self.id
    EXPIRE()
    nA ← Rand(32); tA ← floor(now())
    C ← Challenge(self.id, slot(self.id), nA, tA)
    pend_I[nA] ← (C, peer, now())
    return C

procedure RESPOND(C):
    EXPIRE()
    require len(C.nA) = 32
    CHECK_PEER(C.idA, C.slotA)
    if |now() − C.tA| > W: reject
    if (C.idA, C.nA) ∈ seen: reject            // repetição
    seen[(C.idA, C.nA)] ← C.tA + W
    nB ← Rand(32)
    T ← TRANSCRIPT(C, self.id, slot(self.id), nB)
    tagB ← MAC(K, L_RESP ‖ T)
    pend_R[nB] ← (T ‖ lp(tagB), now(), C.idA)
    return Response(self.id, slot(self.id), C.nA, nB, tagB)

procedure FINISH(R):                           // iniciador
    EXPIRE()
    (C, peer, _) ← pend_I.lookup(R.nA)  or reject   // sem consumir (H-1)
    if R.idB ≠ peer: reject
    CHECK_PEER(R.idB, R.slotB)
    require len(R.nB) = 32
    T ← TRANSCRIPT(C, R.idB, R.slotB, R.nB)
    if not ConstEq(MAC(K, L_RESP ‖ T), R.tagB): reject
    pend_I.remove(R.nA)                         // só após todas as verificações
    U ← T ‖ lp(R.tagB)
    accept(peer = R.idB, sid = MAC(K, L_SESS ‖ U)[0..16))
    return Verify(R.nB, MAC(K, L_VER ‖ U))

procedure COMPLETE(V):                         // respondente
    EXPIRE()
    (U, _, idA) ← pend_R.lookup(V.nB)  or reject    // sem consumir (H-1)
    if not ConstEq(MAC(K, L_VER ‖ U), V.tagA): reject
    pend_R.remove(V.nB)
    accept(peer = idA, sid = MAC(K, L_SESS ‖ U)[0..16))

procedure EXPIRE():
    remove de seen as entradas com instante de expiração anterior a now()
    remove de pend_I e pend_R as entradas com mais de W segundos
```

---

## 9. Modelo de ameaça e propriedades de segurança

### 9.1 Modelo de atacante

Adota-se o modelo **Dolev-Yao**, padrão na análise de protocolos: o atacante controla toda a rede. Ele pode ler, bloquear, atrasar, reordenar, repetir e forjar mensagens, e iniciar quantas execuções quiser com quaisquer nós, em qualquer papel.

O atacante **não** quebra as primitivas criptográficas (premissas C1 e C2 abaixo) e **não** conhece `K`, a menos que ela seja explicitamente comprometida.

### 9.2 Premissas criptográficas

| ID | Premissa |
|---|---|
| C1 | HMAC-SHA-256 com chave secreta uniforme é uma função pseudoaleatória (PRF). Em particular, é infalsificável: sem `K`, não se produz uma tag válida para entrada nova. |
| C2 | Os nonces de 32 bytes não se repetem e não são previsíveis (premissa A5). |

### 9.3 Eventos

Para definir as propriedades, cada execução registra eventos:

- `BeginI(A, B, X, sid)`: A, como iniciador, envia a mensagem 3 sobre os dados `X`.
- `AcceptI(A, B, X, sid)`: A aceita B como respondente, em `FINISH`.
- `BeginR(B, A, X, sid)`: B, como respondente, envia a mensagem 2.
- `AcceptR(B, A, X, sid)`: B aceita A como iniciador, em `COMPLETE`.

Aqui `X = (f0, base, idA, slotA, nA, tA, idB, slotB, nB)` é o conteúdo do transcript `T`, e `sid` é o identificador de sessão derivado na seção 6.4. Os eventos do modelo ProVerif carregam o mesmo par `(T, sid)`.

### 9.4 Propriedades pretendidas

| ID | Propriedade | Definição |
|---|---|---|
| **P1** | Autenticação do respondente (acordo injetivo) | Se A executa `AcceptI(A, B, X)` e `K` não foi comprometida, então B executou `BeginR(B, A, X)` antes, e a cada `AcceptI` corresponde um `BeginR` distinto. |
| **P2** | Autenticação do iniciador (acordo injetivo) | Se B executa `AcceptR(B, A, X)` e `K` não foi comprometida, então A executou `BeginI(A, B, X)` antes, e a cada `AcceptR` corresponde um `BeginI` distinto. |
| **P3** | Vinculação da sessão | Quando A e B aceitam a mesma execução, concordam sobre os identificadores, as fases, os dois nonces, o carimbo de tempo, o contexto (`f0`, `base`) e o `sid`. Na verificação simbólica, o contexto é global (ver 12.4); a rejeição entre nós com contextos divergentes é sustentada por teste, não pelo modelo. |
| **P4** | Sigilo da PSK | O atacante não obtém `K` a partir das execuções do protocolo. No modelo simbólico, esta propriedade decorre diretamente da modelagem do HMAC como MAC simbólico, sem equações nem destrutor (premissa C1) e do fato de `K` nunca ser transmitida; a consulta correspondente funciona como verificação de sanidade do modelo, não como resultado independente. |

O caráter injetivo de P1 e P2 é o que formaliza a resistência a repetição *dentro* do modelo: uma mensagem antiga reenviada não produz uma segunda aceitação.

### 9.5 Propriedades que não são reivindicadas

- **Sigilo futuro (*forward secrecy*):** o comprometimento de `K` compromete as execuções passadas e futuras.
- **Chave de sessão:** o protocolo não estabelece chave para proteger dados.
- **Disponibilidade:** o atacante pode impedir a conclusão de execuções (ver H-1). Isso é inevitável no modelo Dolev-Yao. Antes da correção de H-1, uma única mensagem falsa bastava para cancelar uma execução; após a correção, mensagens inválidas são rejeitadas sem afetar a execução legítima. Além disso, a mensagem 1 não é autenticada por desenho: cada desafio bem formado com identificador de par válido faz o respondente calcular um HMAC e criar estado (ver H-7).
- **Repetição após reinício:** o registro `seen` é volátil.
- **Autenticação entre nós que compartilham a mesma PSK:** fora da premissa A2.
- **Resistência quântica:** HMAC-SHA-256 com chave de 256 bits é considerado robusto contra os ataques quânticos conhecidos, mas esta especificação não reivindica propriedade pós-quântica.
- **Canais laterais e implementação:** fora do escopo, exceto pela comparação em tempo constante (A6).

---

## 10. Achados identificados durante a especificação

| ID | Achado | Efeito | Encaminhamento |
|---|---|---|---|
| **H-1** | `FINISH` e `COMPLETE` removem o estado pendente **antes** de concluir as verificações (linhas 432 e 459 da implementação anterior à correção, commit `e8f15f5`). Em `FINISH`, a remoção precedia também a conferência do par esperado, `check_peer` e o tamanho de `nB` (linhas 436–439 da mesma versão), além da tag. | Quem observa a rede vê `nA` na mensagem 1 e `nB` na mensagem 2 e pode enviar uma Response ou Verify falsa antes da legítima, cancelando a execução. Evidência: reprodução por execução avulsa em 2026-10-21, fora da suíte de testes (após uma Response com tag falsa, a Response legítima foi rejeitada com "no pending challenge"); o teste de regressão será incluído com a correção. Não permite falsificar autenticação (P1–P4 não são afetadas); é uma falha de disponibilidade. | **Corrigido** no micro-sprint seguinte: o estado é consultado sem ser consumido e só é removido após todas as verificações; testes `test_h1_*`. |
| **H-2** | O motor recebe uma única PSK por instância, para todos os pares. | A premissa A2 (PSK por par) só é atendida se a implantação usar uma instância por par. | Registrar como requisito de implantação; considerar na v1.1 um mapa `par → PSK`. |
| **H-3** | `sid` é derivado como um valor pseudoaleatório, mas tem só 16 bytes, é chamado de identificador e não passa por função de derivação de chaves. | Não deve ser usado como chave. | Para estabelecer chave de sessão, definir derivação dedicada (por exemplo HKDF-SHA-256, RFC 5869) em versão futura, com prova própria. |
| **H-4** | O iniciador não verifica o carimbo de tempo da própria execução além da expiração de `pend_I`. | Sem efeito em P1–P4; a expiração em `W` limita a validade. | Nenhum, salvo decisão de projeto. |
| **H-5** | Borda temporal da proteção contra repetição: a janela de aceitação é inclusiva (`|agora − tA| ≤ W`), e a entrada em `seen` expira de forma estrita em `recebimento + 2W`. No instante limite, um desafio ainda aceito pode já não constar de `seen`. | Janela mínima de repetição na fronteira; sem efeito em P1–P4. Identificado por leitura do código; não reproduzido. | **Corrigido**: `seen` passa a reter o identificador até `tA + W`, com expiração inclusiva; teste `test_h5_replay_rejected_at_window_boundary`. |
| **H-6** | A configuração não é validada: `base` = 0 provoca divisão por zero e `base` > 65535 provoca erro de serialização, em vez de `HSLAuthError`; `f0` não finito (NaN) ou `-0.0` gera codificações distintas para valores numericamente "iguais". | Sem efeito com a configuração padrão. Identificado por leitura do código. | **Corrigido**: a configuração valida `f0` (finito e positivo), `base` (inteiro de 1 a 65535) e `timestamp_window` (inteiro positivo); testes `test_h6_*`. |
| **H-7** | O respondente cria estado (`pend_R` por `W`, `seen` até `tA + W`) e calcula um HMAC para cada desafio bem formado, antes de qualquer autenticação; `EXPIRE` reconstrói as estruturas a cada chamada. | Consumo de memória e processamento por quem conheça um identificador de par válido. Disponibilidade não é reivindicada (9.5). | Avaliar limites de estado e de taxa em versão futura. |

---

## 11. Correspondência entre especificação e implementação

| Elemento | Implementação (`hsl/hsl_auth_v1.py`) |
|---|---|
| Constantes e rótulos | linhas 69–84 |
| `slot(id)` | `harmonic_phase_slot`, linhas 96–104 |
| `lp(x)` | `_lp`, linhas 112–114 |
| Decodificação e regras da seção 6.2 | `_Reader`, linhas 124–164 |
| Mensagens 1–3 | `Challenge`, `Response`, `Verify`, linhas 186–275 |
| Validação da configuração (H-6) | `HSLAuthConfig.__post_init__`, linhas 296–320 |
| `T` | `_transcript`, linhas 373–388 |
| `check_peer` | `_check_peer`, linhas 390–396 |
| `EXPIRE` | `_expire`, linhas 398–407 |
| `INITIATE`, `RESPOND`, `FINISH`, `COMPLETE` | linhas 411–516 (métodos públicos com trava e implementações internas) |
| Testes | [`tests/test_hsl_auth_v1.py`](../../tests/test_hsl_auth_v1.py) (51 testes: 32 originais e 19 de regressão para H-1, H-5 e H-6) |

**Implementação de referência desta especificação:** SHA-256 de `hsl/hsl_auth_v1.py` = `f8360e32a4d1e6593f4561a8e83fb1a3546407058d5818aa1885c47fec0e6216`. O workflow `formal` compara esse valor com o arquivo atual e falha se o código mudar sem que esta especificação (incluindo os números de linha acima) seja revista e o valor atualizado.

---

## 12. Verificação formal simbólica (ProVerif)

### 12.1 Objeto e método

As propriedades P1 a P4 foram verificadas com o **ProVerif 2.05**, verificador automático de protocolos criptográficos no modelo simbólico (Dolev-Yao). O modelo cobre:
- execuções ilimitadas e concorrentes, com os dois papéis em cada nó honesto (A e B);
- um terceiro nó C, controlado pelo atacante, com PSKs próprias com A e com B (premissa A2 respeitada);
- dois modelos de controle, nos quais a ferramenta deve encontrar ataque:
  - (i) a mesma PSK compartilhada com C, violando A2;
  - (ii) o respondente deixa de verificar a mensagem 3 (regressão do achado F-05 da auditoria).

Arquivos: [`formal/proverif/`](../../formal/proverif/). A execução ocorre no GitHub Actions (workflow não obrigatório para merge), em [`.github/workflows/formal.yml`](../../.github/workflows/formal.yml). Cada linha de resultado do ProVerif é publicada como anotação da execução, e a saída completa fica no artefato `proverif-results`. O workflow compara a saída de cada modelo, linha a linha, com um gabarito versionado em [`formal/proverif/expected/`](../../formal/proverif/expected/): o conjunto exato de consultas e o resultado de cada uma. Qualquer consulta adicional, ausente, duplicada ou com resultado diferente faz o workflow falhar. Antes da verificação, uma etapa de correspondência confere se `hsl/hsl_auth_v1.py` é a versão registrada na seção 11; se o código mudar, o workflow falha até que esta especificação seja revista. O workflow também roda em alterações na `main`, na especificação, nos modelos e no código de referência.

**Consultas do modelo principal.** São cinco consultas, não cinco propriedades independentes:
- duas consultas de correspondência injetiva para P1 (pares A→B e B→A);
- duas para P2 (pares A→B e B→A);
- uma de sigilo para P4.

P3 não tem consulta própria: está incorporada às quatro consultas de correspondência, cujos eventos carregam o transcript completo e o identificador de sessão.

### 12.2 Resultados

Execução de referência: workflow `formal`, run `39589114061`, commit `994661d0657e69699d9ffcf193024f0b99511153`, com o hash do ProVerif conferido contra o valor fixado. Os resultados abaixo foram transcritos das anotações dessa execução. O commit que registra esta referência altera apenas este parágrafo; os modelos e o workflow são idênticos aos do commit de referência, e o workflow reexecuta a verificação a cada alteração da especificação.

| Modelo | Consulta | Resultado | Esperado |
|---|---|---|---|
| Principal | `inj-event(AcceptI(A,B,t,s)) ==> inj-event(BeginR(B,A,t,s))` (P1) | verdadeiro | verdadeiro |
| Principal | `inj-event(AcceptI(B,A,t,s)) ==> inj-event(BeginR(A,B,t,s))` (P1) | verdadeiro | verdadeiro |
| Principal | `inj-event(AcceptR(B,A,t,s)) ==> inj-event(BeginI(A,B,t,s))` (P2) | verdadeiro | verdadeiro |
| Principal | `inj-event(AcceptR(A,B,t,s)) ==> inj-event(BeginI(B,A,t,s))` (P2) | verdadeiro | verdadeiro |
| Principal | `not attacker(kab)` (P4) | verdadeiro | verdadeiro |
| Controle (i) | as quatro consultas de P1 e P2, inclusive na forma não injetiva | falso (ataque encontrado) | falso |
| Controle (i) | consulta de P4 | ausente | — (a chave é pública neste controle) |
| Controle (ii) | as duas consultas de P2, inclusive na forma não injetiva | falso (ataque encontrado) | falso |
| Controle (ii) | as duas consultas de P1 e a de P4 | verdadeiro | verdadeiro |

O controle (ii) mostra que o modelo discrimina as propriedades: remover a verificação da mensagem 3 quebra apenas a autenticação do iniciador, e as demais continuam valendo.

### 12.3 Ambiente e integridade

| Item | Valor |
|---|---|
| Verificador | ProVerif 2.05 (Blanchet, Cheval e Sylvestre), compilado no runner a partir do pacote-fonte oficial |
| SHA-256 do pacote-fonte | `4871f53c32ab4a04669a060c4886ba5d9080496963fb980a9a62d2c429ceabc4` |
| Fixação | Desde o commit `20e21ec`, anterior ao run de referência, o workflow rejeita qualquer pacote com outro hash; o run de referência foi conferido contra esse valor |

**Limite da fixação:** o hash foi obtido na primeira observação do pacote oficial (modelo *trust on first use*). Ele garante que execuções futuras usem o mesmo pacote, mas não substitui uma conferência contra soma publicada pelos autores ou contra uma distribuição independente. Essa conferência está pendente.

### 12.4 Correspondência entre modelo e implementação

O ProVerif analisa o modelo, não o código Python. A validade das conclusões para a implementação depende das abstrações abaixo.

| Mecanismo da implementação | Tratamento | Evidência |
|---|---|---|
| Conteúdo do transcript `T` (campos e ordem) | Representado diretamente, como tupla simbólica | Modelo; seção 6.3 |
| Serialização em bytes, prefixos de comprimento, decodificação | Abstraído. A tupla simbólica pressupõe codificação injetiva, garantida pelos prefixos de comprimento (seção 6.3) | Testes de implementação `test_f06_*` (ida e volta, bytes truncados e excedentes, tipo errado) |
| Contexto `f0` e `base` | Representado como constantes **globais**: o modelo não contempla nós com configurações diferentes, e a concordância sobre o contexto vale apenas nesse cenário | Teste `test_wrong_context_f0_is_rejected` cobre a divergência de `f0` na implementação; modelar contexto por participante fica para evolução do modelo |
| Separação de domínio pelos rótulos | Representado (constantes distintas) | Modelo; seção 2 (rótulos prefix-distintos) |
| HMAC-SHA-256 | Abstraído como MAC simbólico, sem equações nem destrutor (premissa C1) | Premissa; `test_f02_*` confirma o uso de HMAC com chave |
| Truncamento do `sid` a 16 bytes | Representado como função opaca `trunc16` | Modelo; colisões de 128 bits desconsideradas por premissa |
| Frescor dos nonces | Representado (nomes novos a cada execução) | Modelo; premissa A5 |
| Carimbo de tempo e janela `W` | Abstraído: `tA` é valor público novo; a janela não é modelada | Testes `test_stale_challenge_is_rejected`, `test_expired_pending_challenge_is_rejected` |
| Estado pendente (`pend_I`, `pend_R`) | Representado de forma implícita: cada processo de sessão só aceita a mensagem com seu próprio nonce | Modelo; testes de repetição |
| Ordem de consumo do estado (H-1) | Fora do modelo | Achado H-1 corrigido; testes `test_h1_*` |
| Registro `seen` contra repetição | Fora do modelo. No modelo, a resistência a repetição decorre da correspondência injetiva com nonces frescos | Testes `test_f08_*`, `test_h5_*` |
| Expiração, reinício de processo, concorrência entre threads | Fora do escopo | Declarado na seção 9.5 |
| `check_peer` (identificador próprio, registro, fase) | Representado (`idA <> me`, tabela de chaves, `slot`), **com ressalva**: no modelo a tabela de chaves é por par e sempre obrigatória; no código o registro `peers` é opcional e há uma única PSK por instância (H-2). A correspondência vale para implantações com uma instância do motor por par | Modelo; testes `test_f04_*`, `test_reflection_*` |
| PSK exclusiva por par (A2) | Representado como tabela de chaves por par | Modelo. O controle (i) torna a chave do par conhecida do atacante e mostra que, nesse caso, P1 e P2 deixam de valer; ele não modela um terceiro nó legítimo que compartilhe a mesma PSK |
| Comparação em tempo constante | Fora do escopo | Premissa A6 |

### 12.5 O que a verificação sustenta e o que não sustenta

**Sustenta:** no modelo simbólico, sob as premissas A1–A6 e C1–C2, nenhum atacante que controle a rede consegue fazer um nó honesto aceitar uma execução que o outro nó honesto não realizou com os mesmos dados (P1, P2 e P3), e o sigilo da PSK (P4) se mantém, como consequência direta da modelagem do HMAC (premissa C1).

**Não sustenta:**
- que o código Python inteiro esteja formalmente verificado. A correspondência é estabelecida por revisão (seções 11 e 12.4) e por testes, não por extração automática;
- uma prova computacional por redução, com limites explícitos de vantagem do atacante. Esse é um trabalho distinto, cuja extensão ainda não foi avaliada;
- propriedades de disponibilidade, o mecanismo operacional de prevenção de repetição, nem o comportamento após reinício;
- a rejeição de execuções entre nós com contextos (`f0`, `base`) divergentes, que o modelo não representa.
