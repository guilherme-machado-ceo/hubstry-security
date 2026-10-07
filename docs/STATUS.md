# Technical Status and Limitations

This file is the canonical technical status ledger for the public project overview. The material below preserves the historical status, limitation and research-positioning content moved from the README.

## Current state

| Component | State |
|---|---|
| HSL v0 | Registro histórico |
| HSL Auth v1 (PSK-HMAC) | Experimental, implementado e testado |
| ML-KEM-768, ML-DSA-65, SLH-DSA-SHA2-128s | Provedor experimental na `main`; 19 testes reproduzidos |
| ML-DSA no handshake HSL | Pendente (F-01b) |
| CI (integração contínua) | GitHub Actions com três gates independentes: sintaxe, testes gerais e PQC com backend obrigatório |
| `post-quantum/rho3_bound.py` | Erro de sintaxe corrigido (F-11); módulo continua bloqueado e seus resultados não devem ser citados |
| Digital Laboratory Twin | Planejado |
| Validação adversarial integrada | Pendente |
| TRL 4 | Não estabelecido |
| QPU / CUDA-Q / cuPQC | Trilha de pesquisa separada do gate de segurança |

## Não reivindicado — trilha quântica

**Não reivindicado:** segurança quântica, vantagem quântica, nível criptográfico. `post-quantum/rho3_bound.py`: auditado (Fases 1–2, 2026-10-03) — experimentalmente inválido e cientificamente bloqueado até definição formal de f_ρ₃; não citar resultados do módulo. O bloqueio é da implementação e da quantidade f_ρ₃; o conceito ρ₃ permanece objeto de pesquisa. Registro experimental completo:
[`docs/research/pr1-quantum-encoding.md`](research/pr1-quantum-encoding.md).

## Não reivindicado — HSL

**Não reivindicado:** tamanho de handshake validado, equivalência de segurança com TLS 1.3, resistência quântica, autenticação mútua, adequação validada a qualquer ambiente de aplicação. Auditoria documental completa e achados de implementação:
[`docs/research/hsl-documentation-audit-2026-10.md`](research/hsl-documentation-audit-2026-10.md).

## Escopo atual do provedor PQC e do HSL Auth v1

- O provedor PQC ainda não é usado por nenhum fluxo da plataforma, incluindo o handshake HSL. Não é uma implementação criptograficamente validada. Ver [`post-quantum/README.md`](../post-quantum/README.md).
- O HSL Auth v1 corrige, nesta implementação experimental, os achados F-02 a F-09 da auditoria, com 32 testes; não há revisão criptográfica externa. Não usa assinatura pós-quântica: a integração de ML-DSA ao handshake (F-01b) está pendente. Relatório: [`research/hsl-v1-execution-report-2026-10.md`](research/hsl-v1-execution-report-2026-10.md).

## Registros históricos preservados

As seguintes linhas e descrições fazem parte do histórico do projeto e permanecem aqui como registro:

- **HSL Auth v0:** simulação histórica H-Challenge/Response (meta histórica ~200 B, não validada).
- **π-Radical Operator:** operador π-radical — 6 relações ρ₁-ρ₆. Não presente neste repositório.
- **W Matrix Fixed-Point:** Matriz W — ponto fixo espectral. Não presente neste repositório.
- **Bound ρ₃ Quântico:** limite quântico ρ₃. Bloqueado (auditoria 2026-10-03).

## Meta histórica de aproximadamente 200 bytes

O projeto explorou uma meta de aproximadamente 200 bytes por handshake; esse valor não foi validado experimentalmente. A simulação v0 utiliza uma assinatura simulada como placeholder; a integração de uma assinatura ML-DSA-65 implicará requisitos de tamanho de mensagem significativamente diferentes, a serem medidos no protocolo efetivamente definido. Tamanho efetivo, custo computacional e propriedades de segurança ainda precisam ser medidos e analisados experimentalmente. Aplicações-alvo em investigação: IoT, telecomunicações e ambientes com recursos computacionais restritos.

## Nota sobre prazos

As fases do roadmap original não foram concluídas nos prazos originais e serão replanejadas; as datas originais aparecem apenas como registro histórico; novas datas ainda não foram definidas.

## Exemplo ilustrativo — derivação HALE

> **Ilustrativo e não funcional.** Este trecho não usa ML-KEM: a função calcula `fk` e o descarta, devolvendo o mesmo hash de `f0` para qualquer nível. Mantido como registro histórico; ver auditoria C05.

```python
from hashlib import sha256
import math

def hale_key_derivation(f0, level, b):
    phi = sum(1 for k in range(1, b) if math.gcd(k, b) == 1)
    fk = f0 * (phi ** level)
    return sha256(str(f0).encode()).digest()
```
