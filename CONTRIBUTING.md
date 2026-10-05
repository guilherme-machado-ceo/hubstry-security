# Contributing to Hubstry Security Platform

## [PT-BR] | [EN]

### Como Contribuir / How to Contribute

1. **Fork** este repositório
2. Crie uma branch de feature (`git checkout -b feature/nome-da-feature`)
3. Commit suas alterações (`git commit -m "feat: descrição"`)
4. Push para a branch (`git push origin feature/nome-da-feature`)
5. Abra um **Pull Request**

### Padrões de Commit / Commit Convention

Utilizamos **Conventional Commits**:

- `feat:` nova funcionalidade
- `fix:` correção de bug
- `docs:` alteração de documentação
- `security:` correção de vulnerabilidade
- `refactor:` refatoração sem mudança de comportamento
- `test:` adição ou correção de testes

### Regra de evidência / Evidence rule

Nenhum resultado experimental executado por um único agente (pessoa ou agente de IA) é promovido a evidência de linha de base sem reprodução independente, quando tecnicamente viável. O relatório de reprodução registra ambiente, versões, comandos e resultados, e nunca material secreto.

Fluxo de revisão adotado: implementação → reprodução independente e testes → revisão de arquitetura, segurança e evidência → aprovação do merge pelo pesquisador principal. Exemplo: [`docs/research/hsl-v1-execution-report-2026-10.md`](docs/research/hsl-v1-execution-report-2026-10.md).

*No experimental result produced by a single agent (human or AI) is promoted to baseline evidence without independent reproduction, where technically feasible.*

### Integração contínua / Continuous integration

Todo pull request e todo push na `main` executam três verificações independentes em [`.github/workflows/ci.yml`](.github/workflows/ci.yml):

| Gate | O que verifica |
|---|---|
| `syntax` | `python -m compileall` em `quantum`, `hsl`, `post-quantum` e `tests`; detecta erros de sintaxe em módulos que nenhum teste importa |
| `general-tests` | `pytest tests/`, exceto a suíte PQC |
| `pqc` | liboqs 0.16.0 compilada da fonte e `pytest tests/pqc` com `HUBSTRY_REQUIRE_PQC=1`: backend ausente é falha, não *skip* |

Os três precisam passar antes do merge. "Testes aprovados" em um gate não implica validade do repositório inteiro. O workflow usa token somente leitura e não usa segredos.

*Every pull request and push to `main` runs three independent gates (syntax, general tests, PQC with a required backend). All three must pass before merging.*

### Código de Conduta / Code of Conduct

Seja respeitoso e construtivo. Reporte comportamento inadequado para guilhermemachado.ceo@hubstry.dev.