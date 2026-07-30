# SisTer-Compras

**Nexo-Compras** é um contexto autônomo do **SisTer Nexo**, desenvolvido em
**C++20** e **Python/REST** para governança de necessidades, especificação de
requisitos, cotações, evidências de proveniência, suporte à decisão técnica
supervisionada por IA conversacional e gestão do ciclo de vida de aquisições em
projetos de pesquisa.

## Integração Nexo-Compras

O SisTer Nexo é a autoridade para projetos, ações e atividades de pesquisa.
Este produto integra-se a ele como contexto especializado, recebendo
referências dessas atividades e devolvendo estados resumidos de necessidades,
decisões e atendimento.

**Nexo-Compras** é o nome de produto integrado; o identificador técnico
`sister_compras` é preservado por compatibilidade.
Compras continuará com processo, banco, contratos e regras próprios. A proposta,
os dados compartilháveis e os impedimentos estão na
[ADR-005](adr/ADR-005-nexo-compras-federated-boundary.md) e em
[SISTER_INTEGRATION.md](SISTER_INTEGRATION.md).

A integração usa `nexo-compras.integration/1.0.0` e API contratual com o Nexo.
O SisTer autentica o acesso ao Nexo, e o Nexo encaminha a identidade ao Compras.
Nenhuma tabela ou credencial é compartilhada.

A aba **Acordo com Nexo** permite aceitar ou contrapropor capacidades e
acompanhar recibos e histórico. O protocolo é
`sister.integration-agreement/1.0.0`, especializado pelo perfil
`nexo-compras.profile/1.0.0`. Dados de integração só são expostos quando a
capacidade correspondente estiver aceita em um acordo ativo.

```text
              SisTer
                ↓
       SisTer Nexo (projetos)
                ↓
          Nexo-Compras
              ↓
especificação, evidências, cotações,
decisão técnica, lista de compras e entregas
```

## Repositório e Controle de Versão

- **GitHub Remote:** `git@github.com:jpereiratrindade/sister-compras.git`
- **Política de Versionamento:** Semantic Versioning com tags Git anotadas padrão (`v0.1.0`, `v0.2.0`, `v0.3.0`, `v0.4.0`, ...).
- **Versão Atual:** `0.4.0` (definida em `VERSION` e `CMakeLists.txt`).

### Convenção de Tags Git

As tags seguem o padrão anotado Semantic Versioning:

```bash
# Criar tag de release v0.4.0
git tag -a v0.4.0 -m "release: v0.4.0 - Nexo-Compras federado"

# Enviar branch principal e tags para o GitHub
git push origin main --tags
```

---

## Recursos da Versão 0.4.0

1. **Banco PostgreSQL 17 dedicado (`nexo-compras-dev-db:55440`):**
   - Container Podman/Docker exclusivo e isolado para o SisTer-Compras.
   - Sincronização nativa SQL (`UPSERT`) em tempo real para todas as necessidades, cotações e pareceres de decisão.
2. **Assistente Conversacional RAG Multi-Turno (`qwen2.5:14b`):**
   - Memória conversacional entre turnos com preservação do título, quantidade, categoria e prioridade.
   - Parsing automático de moeda brasileira (ex: *"80,00"*, *"R$ 80"*) para o parâmetro numérico `estimated_budget`.
3. **Edição Inteligente de Registros Existentes (`update_need`):**
   - Mapeamento via RAG para identificação de recursos já cadastrados no banco.
   - Atualização direta de registros sem duplicação de IDs.
4. **Exibição Orçamentária Prevista em R$:**
   - Tabela da Lista de Compras calcula automaticamente subtotais previstos com badge `(Estimado)` antes das cotações finais.
5. **Trava de Persistência de Dados:**
   - Script orquestrador `./scripts/run_all.sh` verifica o estado existente e impede a sobrescrita acidental por re-seeding.

---

## Comando Único de Execução (Full Cycle)

Para compilar o projeto C++20, rodar todos os testes automatizados, validar contratos de governança, subir o banco de dados PostgreSQL independente e iniciar a **Interface Web** em um único comando:

```bash
./scripts/run_all.sh dev 8016
```

Acesse pelo SisTer autenticado em:
**`http://localhost:8000/integrations/nexo/compras/`**.

A marca **Nexo-Compras**, no canto superior esquerdo, retorna à visão geral do
Compras. A ação **Voltar ao Nexo**, separada ao fim da navegação lateral,
restabelece explicitamente o contexto do subsistema integrador.

A origem `http://127.0.0.1:8016` permanece em loopback e recusa acesso sem a
identidade federada. O acervo operacional autenticado é listado integralmente
no Compras e cada necessidade exibe sua referência de projeto. Toda nova
necessidade e toda reatribuição exigem a seleção de um projeto cadastrado no
Nexo. Projeções enviadas ao Nexo e operações sobre um projeto continuam
sujeitas ao acordo e à autorização local correspondente.

---

## Princípios Arquiteturais

1. **Necessidade antes do produto:** A engenharia da decisão e os requisitos pertencem ao projeto; os produtos comerciais são transitórios.
2. **Separação epistemológica:** Distinção explícita entre dados de fabricantes, cotações observadas, extrações de IA e pareceres de decisão de pesquisadores humanos.
3. **Auditabilidade & Proveniência:** Registro de fonte, data de consulta, responsável e estado de verificação em cada evidência técnica.
4. **Governança por Contratos:** Intercâmbio de necessidades e pareceres via esquema JSON Schema federado (`contracts/sister_compras_manifest.schema.json`).

## Modelo de Domínio (DDD + C++20)

- `domain::Project`: Projeto de pesquisa, responsável técnico e centros de custo.
- `domain::Need`: Agregado raiz de necessidade (categoria, quantidade, prioridade, status, orçamento estimado).
- `domain::Requirement`: Requisitos obrigatórios, desejáveis, regulatórios, de segurança e logística.
- `domain::Alternative`: Produtos comerciais, serviços, desenvolvimentos internos e aluguéis.
- `domain::Evidence`: Registros de proveniência, confiança e validação por especialistas.
- `domain::PriceObservation`: Cotações temporais de fornecedores com moeda e URL.
- `domain::Decision`: Decisão formal registrada por pesquisador com justificativa técnica.

## Compilação e Testes Manuais

```bash
# Configurar build
cmake -S . -B build

# Compilar
cmake --build build

# Executar suíte de testes CTest
ctest --test-dir build --output-on-failure
```

## Validação de Governança

```bash
python3 scripts/validate_tool_contracts.py
python3 scripts/validate_governance_repo.py
```
