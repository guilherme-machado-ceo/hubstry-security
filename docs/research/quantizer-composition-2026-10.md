# Composição de quantizadores e regra de hierarquia de grades de fase (HALE-Q)

**Data:** 2026-10-21
**Código:** [`quantum/quantizer_composition.py`](../../quantum/quantizer_composition.py) · **Testes:** [`tests/test_quantizer_composition.py`](../../tests/test_quantizer_composition.py)
**Fonte:** artigo de trabalho "A Theory of Quantizer Composition", v1.0, de autoria de Guilherme Gonçalves Machado (Hubstry Deep Tech).
**Escopo:** verificação computacional com aritmética racional exata (`fractions.Fraction`), sem ponto flutuante em nenhuma decisão. Sem processador quântico.

> **EN summary.** Reading a phase address on a fine grid n and then re-reading it on a coarse grid m by nearest-point rounding agrees with a direct coarse reading if and only if n/m is an odd integer (for m ≥ 2). Floor quantizers only need m | n. The fraction of phases that land on a different coarse address (μ) has exact closed forms, which differ between the interval [0, 1) and the circle (the natural domain for phases). This record verifies the working paper's theorems with exact arithmetic over finite ranges, records the corrections found (the m = 1 edge case, the interval-domain formulas and further items listed in section 3.1), and states the result as a design rule for HALE-Q grid hierarchies. When n/m is odd the agreement is pointwise, not only almost everywhere. Finite verification is regression evidence, not a general proof. No security or quantum claim is made.

## 1. Pergunta

O HALE-Q endereça por fases θ_k = 2πk/n numa grade de *n* pontos. Quando um sistema lê o endereço numa grade fina (*n*) e depois o converte para uma grade grossa (*m*) por arredondamento ao ponto mais próximo, o resultado coincide com a leitura direta na grade grossa? E, se não coincide, em que fração das fases ocorre a divergência?

## 2. Definições

- **Piso:** Q_n(x) = ⌊n·x⌋/n, em [0, 1).
- **Arredondamento (meio para cima):** R_n(x) = arred(n·x)/n, em dois domínios:
  - **intervalo** [0, 1): o resultado é limitado a (n−1)/n para permanecer em [0, 1);
  - **círculo** ℝ/ℤ: o resultado é tomado módulo 1. É o domínio natural para fases (θ = 2πx).
- **Divergência:** μ(m, n) = medida de Lebesgue do conjunto {x : A_m(A_n(x)) ≠ A_m(x)}.

O cálculo de μ é exato: as duas funções são constantes entre múltiplos consecutivos de 1/(2m) e 1/(2n), e cada trecho é avaliado no ponto médio.

## 3. Resultados e situação

| Resultado | Enunciado | Situação |
|---|---|---|
| Teorema 1 (piso) | Q_m∘Q_n = Q_m ⇔ m divide n | Teorema do artigo; verificado para m ≤ 24, n ≤ 60 |
| Teorema 2 (arredondamento) | R_m∘R_n = R_m q.t.p. ⇔ n/m é inteiro ímpar, **para m ≥ 2**; com n/m ímpar, a igualdade vale em todo ponto | Teorema do artigo, com correção; verificado nos dois domínios para 2 ≤ m ≤ 24, n ≤ 60; igualdade pontual verificada em todos os pontos de quebra e pontos médios |
| Caso m = 1 | R_1 é constante; R_1∘R_n = R_1 para todo *n* | Correção ao Teorema 2 |
| μ, razão par (círculo) | m/(2n), para m ≥ 2 | Valor que o artigo atribui ao intervalo; correto apenas no círculo; verificado |
| μ, razão par (intervalo) | (m−1)/(2n) | Fórmula corrigida; verificada |
| μ, razão não inteira (círculo) | Σ_{j=0}^{m−1} d_j, para m ≥ 2 | Valor que o artigo atribui ao intervalo; correto apenas no círculo; verificado |
| μ, razão não inteira (intervalo) | Σ_{j=0}^{m−2} d_j | Fórmula corrigida; verificada |
| μ, n divide m, n < m (círculo) | 1 − n/m | Valor que o artigo atribui ao intervalo; correto apenas no círculo; verificado para m < 48 |
| μ, n divide m, n < m (intervalo) | 1 − n/m + 1/(2m) | Fórmula corrigida; verificada para m < 48 |
| n < m sem divisibilidade | Equivalência já decidida pelo Teorema 2 (μ > 0 para m ≥ 2); valor de μ dado pela fórmula por células (seção 3.2); sem forma aritmética fechada | Fórmula proposta na auditoria; verificada; aguarda revisão humana |

Em que d_j é a distância da fronteira b_j = (j + 1/2)/m de R_m até a aresta de Voronoi (k + 1/2)/n mais próxima de R_n.

**Origem das correções.** No intervalo, o limite em (n−1)/n elimina a última fronteira de R_m (a que separaria o último ponto do retorno a 0). Por isso a soma vai até m − 2. Para n > m ≥ 2, o círculo diverge mais que o intervalo por exatamente d_0, que vale 1/(2n) apenas na razão par. Para n divisor de m, n < m, ocorre o inverso: o intervalo diverge mais, por 1/(2m). Os testemunhos do artigo dependem do domínio: no círculo, μ(24, 36) = 1/6 e μ(12, 24) = 1/4; no intervalo, 23/144 e 11/48.

### 3.1 Auditoria matemática de 21/10/2026

O artigo v1.0 foi auditado item por item (37 itens), com implementação independente e demonstrações escritas. Além das correções acima, a auditoria registrou:

- os valores do resumo e do Exemplo 1 são os do círculo, embora o artigo declare o intervalo;
- a justificativa do Corolário 2a ("a prova é local e idêntica") é falsa perto de b_{m−1}, que só é fronteira no círculo;
- a frase de que o limite "não afeta os teoremas" vale para a classificação, mas não para os valores de μ;
- a comutação com a reflexão (Seção 7) vale no círculo e falha no intervalo num conjunto de medida 1/n;
- a fórmula da soma das distâncias não vale em geral para n < m (no círculo, m = 5, n = 2: μ = 3/5, soma = 13/20).

Contraexemplos exatos às fórmulas do artigo no intervalo: m = 2, n = 4 dá 1/8 (o artigo dá 1/4); m = 2, n = 3 dá 1/12 (a soma até j = m − 1 dá 1/6); m = 2, n = 1 dá 3/4 (o artigo dá 1/2). Todos estão cobertos por testes.

### 3.2 Fórmula por células (proposta, em revisão)

Para cada célula [a, e) de R_n com imagem g, e J o conjunto de saltos de R_m no domínio, a contribuição de cada lado é limitada à própria célula:

- lado esquerdo: max(0, min(β, e) − a), com β = max(J ∩ (min(a, g), g]);
- lado direito: max(0, e − max(a, g, α)), com α = min(J ∩ (g, e)).

A soma das contribuições é μ, para todo m e n no intervalo e para m ≥ 2 no círculo. A limitação à célula foi introduzida na revisão cruzada: na redação original, sem ela, a fórmula depende de a imagem g pertencer à célula. Se o trecho do limite [1 − 1/(2n), 1) for tratado como célula própria, a fórmula sem limitação falha (m = 10, n = 2: o termo direito daria 9/20 numa célula de comprimento 1/4). A versão limitada dá o valor exato nas duas leituras, com zero violações em 1 ≤ m ≤ 16, 1 ≤ n ≤ 48, nos dois domínios. Quando cada meia-célula contém no máximo uma fronteira, a fórmula se reduz à soma das distâncias, o que cobre todo o regime n > m.

**Exemplos do artigo confirmados nos dois domínios:**

- R_2∘R_3(0,24) ≠ R_2(0,24);
- R_24∘R_36(0,066) ≠ R_24(0,066);
- dependência de caminho: 36 → 12 → 24 leva 0,066 a 2/24, enquanto 36 → 24 leva a 1/24.

## 4. Regra de hierarquia para o HALE-Q

Saída de `python -m quantum.quantizer_composition` (domínio do círculo):

| Grade fina | Grade grossa | Razão | Consistente | μ |
|---|---|---|---|---|
| 36 | 12 | 3 | sim | 0 |
| 60 | 12 | 5 | sim | 0 |
| 24 | 12 | 2 | não | 1/4 |
| 48 | 12 | 4 | não | 1/8 |
| 36 | 24 | 3/2 | não | 1/6 |
| 18 | 12 | 3/2 | não | 1/6 |
| 72 | 24 | 3 | sim | 0 |
| 256 | 64 | 4 | não | 1/8 |
| 192 | 64 | 3 | sim | 0 |

**Leitura.** Numa hierarquia de grades de fase lida por arredondamento ao ponto mais próximo, cada nível deve ser um múltiplo **ímpar** do nível abaixo. Hierarquias binárias (razão 2 ou 4, como 256 → 64) produzem endereços grossos divergentes numa fração fixa das fases, embora a divisibilidade se mantenha. Se a leitura for por piso (truncamento), basta a divisibilidade.

## 5. O que este registro não afirma

- A verificação cobre faixas finitas de *m* e *n*; é evidência de regressão, não demonstração geral. As demonstrações gerais pertencem ao artigo e dependem da revisão matemática da versão corrigida.
- As demonstrações das fórmulas do intervalo (Teoremas A e B), da comparação com o círculo (Teorema A′) e da fórmula por células foram redigidas na auditoria de 21/10/2026 e aguardam revisão humana antes de entrar na versão 1.1 do artigo. Não estão neste repositório.
- Não há afirmação de segurança, de dificuldade computacional nem de vantagem quântica.

## 6. Reprodução

```bash
python -m quantum.quantizer_composition
python -m pytest tests/test_quantizer_composition.py -v
```

Tempo típico da suíte: cerca de 25 segundos numa CPU comum, sem dependências além da biblioteca padrão e do pytest.
