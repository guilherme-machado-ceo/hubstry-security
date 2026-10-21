# Capacidade de endereçamento de codificações harmônicas de fase (HALE-Q)

**Data:** 2026-10-21
**Código:** [`quantum/capacity.py`](../../quantum/capacity.py) · **Testes:** [`tests/test_capacity.py`](../../tests/test_capacity.py)
**Escopo:** simulação em NumPy. Sem processador quântico, sem CUDA-Q, sem nuvem.

> **EN summary.** For n harmonic addresses θ_k = 2πk/n, the optimal probability of identifying the address from a single equatorial qubit is 2/n and the accessible information is at most 1 bit (Holevo bound), whatever n is. The repository's reference encoding reaches only 2 − (3/4)·log₂3 ≈ 0.8113 bits for every n ≥ 3. An n-level system (qudit) with discrete-Fourier states makes all n addresses perfectly distinguishable (log₂ n bits). The closed forms are known results or direct derivations, verified numerically by the test suite. No security, quantum-advantage or hardware claim is made.

## 1. Pergunta

O experimento PR1 ([`pr1-quantum-encoding.md`](pr1-quantum-encoding.md)) mostrou que, na codificação equatorial, a fidelidade entre endereços vizinhos não depende da posição na grade. A pergunta seguinte é quantitativa: **quantos endereços harmônicos podem de fato ser recuperados de uma codificação quântica**, e como a resposta muda entre um único qubit e um sistema de *n* níveis (qudit).

## 2. Codificações comparadas

Para *n* endereços equiprováveis, com θ_k = 2πk/n:

| Codificação | Estado | Dimensão |
|---|---|---|
| Referência (`quantum/harmonic_state.py`) | cos(θ/2)\|0⟩ + e^{iθ} sin(θ/2)\|1⟩ | 2 |
| Equatorial | (\|0⟩ + e^{iθ}\|1⟩)/√2 | 2 |
| Qudit (estados de Fourier discreta) | (1/√n) Σ_j e^{2πijk/n}\|j⟩ | *n* |

## 3. Grandezas

- **Fidelidade entre vizinhos:** \|⟨ψ_k\|ψ_{k+1}⟩\|².
- **Probabilidade de acerto da medição de raiz quadrada (SRM, *square-root measurement*).** Para conjuntos simétricos (geometricamente uniformes), como as codificações equatorial e de qudit, a SRM é a medição ótima de erro mínimo (Ban et al., 1997; Eldar e Forney, 2001). Para a codificação de referência, que não é simétrica, o valor é apenas um limite inferior do ótimo.
- **Quantidade de Holevo χ:** entropia de von Neumann do estado médio, em bits. É o limite superior da informação acessível por medição (Holevo, 1973).

## 4. Formas fechadas (DERIVADAS) e verificação numérica

| Codificação | Acerto ótimo | χ (bits) | Situação |
|---|---|---|---|
| Equatorial | 2/n (n ≥ 2) | 1 (n ≥ 2) | Resultado conhecido; verificado numericamente para *n* de 2 a 256 |
| Qudit | 1 | log₂ n | Estados ortonormais; verificado numericamente |
| Referência | (limite inferior SRM, numérico) | 2 − (3/4)·log₂3 ≈ 0,8113 para todo n ≥ 3 | Derivação direta, abaixo; verificada numericamente |

**Derivação para a codificação de referência.** Para n ≥ 3, as médias de cos θ, sen θ, cos 2θ e sen 2θ sobre a grade se anulam, e o estado médio é

ρ = [[1/2, −i/4], [i/4, 1/2]],

com autovalores 3/4 e 1/4. Logo χ = H(1/4) = 2 − (3/4)·log₂3 ≈ 0,8113 bit, independentemente de *n*. A codificação de referência não atinge sequer o limite de 1 bit de um qubit.

A fidelidade entre vizinhos da codificação de referência segue a forma fechada F(k, n) = cos⁴(π/n) + sen²(π/n)·cos²((2k+1)π/n), verificada para *n* de 4 a 256 e conferida contra o módulo de base `quantum/harmonic_state.py`.

## 5. Resultados

Saída de `python -m quantum.capacity` (valores arredondados):

| n | Codificação | Fidelidade vizinha (mín. → máx.) | Acerto | χ (bits) |
|---|---|---|---|---|
| 8 | Referência | 0,7500 → 0,8536 | 0,2360 (limite inferior) | 0,8113 |
| 8 | Equatorial | 0,8536 | 0,2500 | 1,0000 |
| 8 | Qudit | 0 | 1,0000 | 3,0000 |
| 12 | Referência | 0,8750 → 0,9330 | 0,1574 (limite inferior) | 0,8113 |
| 12 | Equatorial | 0,9330 | 0,1667 | 1,0000 |
| 12 | Qudit | 0 | 1,0000 | 3,5850 |
| 64 | Referência | 0,9952 → 0,9976 | 0,0295 (limite inferior) | 0,8113 |
| 64 | Equatorial | 0,9976 | 0,0312 | 1,0000 |
| 64 | Qudit | 0 | 1,0000 | 6,0000 |
| 256 | Referência | 0,9997 → 0,9998 | 0,0074 (limite inferior) | 0,8113 |
| 256 | Equatorial | 0,9998 | 0,0078 | 1,0000 |
| 256 | Qudit | 0 | 1,0000 | 8,0000 |

## 6. Leitura dos resultados

1. **Um único qubit não sustenta endereçamento harmônico fino.** Com *n* endereços, a melhor medição acerta com probabilidade 2/n, e nenhuma estratégia extrai mais de 1 bit por medição. Aumentar *n* torna os vizinhos menos distinguíveis, não mais endereçáveis.
2. **A codificação equatorial é a melhor codificação de qubit entre as comparadas.** Além da uniformidade posicional registrada no PR1, ela atinge o limite de 1 bit, que a codificação de referência não atinge.
3. **Qudits são a direção física coerente para o HALE-Q.** Com *n* níveis, os mesmos *n* endereços gerados por simetria são ortogonais e perfeitamente distinguíveis, com log₂ n bits por medição.

## 7. O que este registro não afirma

- Não há execução em hardware quântico.
- Não há afirmação de segurança, de vantagem quântica nem de resultado fundamental novo. As fórmulas da codificação equatorial e do qudit são conhecidas; a contribuição é a aplicação ao endereçamento harmônico do HALE, a derivação para a codificação de referência do repositório e a medição comparativa reproduzível.
- Os valores de acerto da codificação de referência são limites inferiores, não ótimos.

## 8. Reprodução

```bash
python -m quantum.capacity
python -m pytest tests/test_capacity.py -v
```

## 9. Referências

- A. S. Holevo, "Bounds for the quantity of information transmitted by a quantum communication channel", *Problems of Information Transmission* 9 (1973).
- M. Ban, K. Kurokawa, R. Momose, O. Hirota, "Optimum measurements for discrimination among symmetric quantum states and parameter estimation", *International Journal of Theoretical Physics* 36 (1997).
- Y. C. Eldar, G. D. Forney, "On quantum detection and the square-root measurement", *IEEE Transactions on Information Theory* 47(3) (2001).
