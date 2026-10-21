# Titularidade, anterioridade e inventário de ativos

> **EN summary.** Technical record of the assets in this repository, their first commits and their incorporation into `main`, as of the reference snapshot `e6fc0ceea1f958d50ebeaa7aeb41fdaf2dd16a27` (2026-10-21). Ownership is declared by Hubstry Deep Tech. This file is an inventory and priority record; it is not a legal instrument and does not create, transfer or prove rights by itself. AI tools were used as instruments under the direction of the principal investigator; Git authorship metadata recording "Claude" on 20 commits of 2026-10-05 is preserved as technical metadata and is not a statement about legal authorship or ownership.

## 1. Natureza deste documento

Este arquivo é um **registro técnico de inventário e anterioridade**. Ele descreve o que existe no repositório, quando cada ativo foi registrado e como chegou à branch principal.

Não é um instrumento jurídico de constituição, cessão ou licenciamento de direitos. A titularidade é **declarada** pela Hubstry Deep Tech; nem este documento nem o histórico do Git substituem os instrumentos jurídicos pertinentes, como contratos, registros e licenças.

## 2. Titular declarado e licença

| Item | Valor |
|---|---|
| Titular declarado | Hubstry Deep Tech |
| Autor e pesquisador principal | Guilherme Gonçalves Machado (ORCID [0009-0008-1083-0784](https://orcid.org/0009-0008-1083-0784)) |
| Contato | guilhermemachado.ceo@hubstry.dev |
| Licença do repositório | CC BY-NC-SA 4.0, conforme [`LICENSE`](../LICENSE) ("Copyright (c) 2023-2026 Hubstry Deep Tech") |

## 3. Snapshot de referência

| Item | Valor |
|---|---|
| Commit | `e6fc0ceea1f958d50ebeaa7aeb41fdaf2dd16a27` |
| Data | 21/10/2026 |
| Conteúdo | Estado da `main` após o merge do PR #15 |

O histórico do Git comprova a **sequência e as datas dos commits** registrados neste repositório. Ele não comprova, por si só, a data de criação intelectual de cada ativo, que pode ser anterior ao primeiro commit. A condição de propriedade intelectual preexistente em relação a programas externos depende dos entendimentos firmados com cada programa e de sua formalização contratual.

## 4. Inventário de ativos

**Critério das datas.** Duas colunas, sem mistura de critérios:

- **Primeiro commit:** commit que introduz pela primeira vez os arquivos principais do ativo no repositório, com a data de autoria registrada no Git.
- **Incorporação à `main`:** pull request e data de merge na branch principal. Os commits iniciais de 24/04/2026 foram feitos diretamente na `main`, sem pull request.

| Ativo | Arquivos principais | Primeiro commit | Incorporação à `main` |
|---|---|---|---|
| Plataforma inicial: documentação, catálogo de vetores de ataque, mapeamento regulatório, roadmap | `docs/`, `attack-vectors/`, `compliance/`, `roadmap/` | `bf8e23b`, 24/04/2026 | Direto na `main`, 24/04/2026 |
| HSL v0 (simulação histórica), detecção de intrusão por desvio de fase, rotação de chaves por LFSR | `hsl/hsl_module.py`, `hsl/intrusion_detection.py`, `hsl/lfsr_key_rotation.py` | `4b4adba`, 24/04/2026 | Direto na `main`, 24/04/2026 |
| Trilha quântica: comparação de codificações de fase e lattice de 64 perfis | `quantum/` | `4682c73`, 02/10/2026 | PR #2, 02/10/2026 |
| Provedor de criptografia pós-quântica (integração da liboqs, transcript canônico, derivação de chaves) | `post-quantum/pqc_provider.py`, `post-quantum/oqs_adapter.py` | `561a14d`, 02/10/2026 | PR #5, 05/10/2026 |
| HSL Auth v1 (PSK-HMAC) | `hsl/hsl_auth_v1.py`, `tests/test_hsl_auth_v1.py` | `e8f15f5`, 05/10/2026 (metadado de autor: ver seção 6) | PR #7, 05/10/2026 |
| Integração contínua com três verificações obrigatórias | `.github/workflows/ci.yml` | `2e82b4c`, 05/10/2026 (metadado de autor: ver seção 6) | PR #9, 05/10/2026 |
| Especificação formal do HSL Auth v1 e modelos ProVerif | `docs/specs/hsl-auth-v1-spec.md`, `formal/proverif/`, `.github/workflows/formal.yml` | `fff050f`, 21/10/2026 | PR #11, 21/10/2026 |
| Correções H-1, H-5 e H-6 do HSL Auth v1 | `hsl/hsl_auth_v1.py`, `tests/test_hsl_auth_v1.py` | `994661d`, 21/10/2026 | PR #13, 21/10/2026 |
| Capacidade de endereçamento do HALE-Q (probabilidade de acerto pela medição de raiz quadrada (SRM, *square-root measurement*), ótima para as codificações simétricas e apenas limite inferior para a codificação de referência; quantidade de Holevo por codificação) | `quantum/capacity.py`, `tests/test_capacity.py`, `docs/research/hale-q-capacity-2026-10.md` | `cc8a75c`, 21/10/2026 | PR #18, 21/10/2026 |
| Composição de quantizadores e regra de hierarquia de grades do HALE-Q (verificação exata) | `quantum/quantizer_composition.py`, `tests/test_quantizer_composition.py`, `docs/research/quantizer-composition-2026-10.md` | `915dca6`, 21/10/2026 | PR #19, 21/10/2026 |

**Origem conceitual.** O HALE (Harmonic Addressing & Labeling Equation) é o framework matemático de autoria do pesquisador principal do qual derivam as linhas HSL e HALE-Q. Ele é externo a este repositório. A versão examinada aqui é *HALE: Harmonic Addressing & Labeling Equation — A General-Purpose Mathematical Framework for Complex Systems*, Version 3.0, 2026, registrada em [`docs/research/hale-audit.md`](research/hale-audit.md); o DOI dessa versão ainda não foi atribuído e não é inferido. As demais publicações do autor estão listadas no perfil ORCID indicado na seção 2.

**Origem da teoria de composição de quantizadores.** Os teoremas verificados no módulo `quantum/quantizer_composition.py` provêm do artigo de trabalho *A Theory of Quantizer Composition*, versão 1.0, de autoria do pesquisador principal, externo a este repositório. O repositório registra a verificação computacional e as correções identificadas (caso m = 1 e fórmulas do domínio intervalo). A verificação por faixas finitas não substitui as demonstrações gerais nem comprova titularidade. A titularidade é declarada na seção 2 deste documento; sua comprovação jurídica depende dos instrumentos aplicáveis. O histórico Git registra a sequência dos commits e a incorporação dos ativos ao repositório, sem constituir, isoladamente, prova de titularidade.

## 5. Componentes e ferramentas de terceiros

Os itens abaixo não são ativos da Hubstry Deep Tech e permanecem sujeitos às suas próprias licenças e atribuições:

| Componente | Uso no repositório |
|---|---|
| liboqs (Open Quantum Safe) e liboqs-python | Implementação dos algoritmos ML-KEM, ML-DSA e SLH-DSA usada pelo provedor pós-quântico |
| ProVerif 2.05 | Verificador formal executado no GitHub Actions; não é distribuído com o repositório |
| Python, pytest, numpy e demais dependências | Ambiente de execução e testes |
| GitHub Actions | Infraestrutura de integração contínua |

Os padrões NIST FIPS 203, 204 e 205 e as referências técnicas citadas na documentação pertencem aos seus respectivos autores e organismos.

## 6. Uso de ferramentas de IA e metadados de autoria

O repositório foi desenvolvido com o apoio de ferramentas de inteligência artificial, usadas como **instrumentos sob a direção do pesquisador principal**. O pesquisador principal definiu o escopo de cada etapa, aprovou os planos, revisou os resultados e autorizou cada merge na `main`.

**Metadados preservados.** Em 05/10/2026, 20 commits, de `9b4343b` a `3a000ee`, registram "Claude" no campo de autor do Git. Esse registro decorre da configuração padrão da ferramenta usada naquele momento. Esses commits foram incorporados à `main` por meio dos PRs #4 a #9, todos aprovados pelo pesquisador principal. Desde então, os commits são registrados com a identidade do pesquisador principal, que dirige e aprova o trabalho.

O histórico **não foi reescrito**, para preservar a integridade dos identificadores de commit citados na documentação técnica e em artefatos já distribuídos.

Os campos de autoria do Git são metadados técnicos. Não constituem conclusão jurídica sobre autoria ou titularidade, e não são usados neste documento como prova dela.

## 7. Reforços externos de rastreabilidade

O snapshot de referência pode ser reforçado por:
- uma *release* do GitHub marcada no commit de referência;
- o registro do identificador do commit em serviço de ancoragem temporal;
- o depósito da release no Zenodo, com DOI.

Esses registros comprovam a existência do conteúdo do repositório numa data. Não comprovam, por si sós, que cada ativo foi criado ou publicado pela primeira vez nessa data.
