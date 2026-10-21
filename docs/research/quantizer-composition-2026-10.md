# Composição de quantizadores e regra de hierarquia de grades de fase (HALE-Q)

**Data:** 2026-10-21
**Código:** [`quantum/quantizer_composition.py`](../../quantum/quantizer_composition.py) · **Testes:** [`tests/test_quantizer_composition.py`](../../tests/test_quantizer_composition.py)
**Fonte:** artigo de trabalho "A Theory of Quantizer Composition", v1.0, de autoria de Guilherme Gonçalves Machado (Hubstry Deep Tech).
**Escopo:** verificação computacional com aritmética racional exata (`fractions.Fraction`), sem ponto flutuante em nenhuma decisão. Sem processador quântico.

> **EN summary.** Reading a phase address on a fine grid n and then re-reading it on a coarse grid m by nearest-point rounding agrees with a direct coarse reading if and only if n/m is an odd integer (for m ≥ 2). Floor quantizers only need m | n. The fraction of phases that land on a different coarse address (μ) has exact closed forms, which differ between the interval [0, 1) and the circle (the natural domain for phases). This record verifies the working paper's theorems with exact arithmetic over finite ranges, records two corrections (the m = 1 edge case and the interval-domain formulas), and states the result as a design rule for HALE-Q grid hierarchies. Finite verification is regression evidence, not a general proof. No security or quantum claim is made.

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
| Teorema 2 (arredondamento) | R_m∘R_n = R_m q.t.p. ⇔ n/m é inteiro ímpar, **para m ≥ 2** | Teorema do artigo, com correção; verificado nos dois domínios para 2 ≤ m ≤ 24, n ≤ 60 |
| Caso m = 1 | R_1 é constante; R_1∘R_n = R_1 para todo *n* | Correção ao Teorema 2 |
| μ, razão par (círculo) | m/(2n) | Fórmula do artigo; verificada |
| μ, razão par (intervalo) | (m−1)/(2n) | Fórmula corrigida; verificada |
| μ, razão não inteira (círculo) | Σ_{j=0}^{m−1} d_j | Fórmula do artigo; verificada |
| μ, razão não inteira (intervalo) | Σ_{j=0}^{m−2} d_j | Fórmula corrigida; verificada |
| μ, n divide m, n < m (círculo) | 1 − n/m | Fórmula do artigo; verificada para m < 48 |
| μ, n divide m, n < m (intervalo) | 1 − n/m + 1/(2m) | Fórmula corrigida; verificada para m < 48 |
| n < m sem divisibilidade | Sem forma fechada | Não classificado |

Em que d_j é a distância da fronteira b_j = (j + 1/2)/m de R_m até a aresta de Voronoi (k + 1/2)/n mais próxima de R_n.

**Origem das correções.** No intervalo, o limite em (n−1)/n elimina a última fronteira de R_m (a que separaria o último ponto do retorno a 0). Por isso a soma vai até m − 2 e a razão par perde meia célula: a diferença entre círculo e intervalo é exatamente 1/(2n). Os testemunhos do artigo dependem do domínio: no círculo, μ(24, 36) = 1/6 e μ(12, 24) = 1/4; no intervalo, 23/144 e 11/48.

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
- As fórmulas corrigidas do intervalo foram derivadas e verificadas computacionalmente; a demonstração formal dessas fórmulas ainda não foi escrita.
- Não há afirmação de segurança, de dificuldade computacional nem de vantagem quântica.

## 6. Reprodução

```bash
python -m quantum.quantizer_composition
python -m pytest tests/test_quantizer_composition.py -v
```

Tempo típico da suíte: cerca de 15 segundos numa CPU comum, sem dependências além da biblioteca padrão e do pytest.
