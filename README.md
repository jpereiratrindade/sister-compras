# SisTer-Compras

**SisTer-Compras** é um subsistema federado autônomo do ecossistema **SisTer** desenvolvido em **C++20** e **Python/REST** para governança de necessidades, especificação de requisitos, cotações, evidências de proveniência, suporte à decisão técnica supervisionada por IA conversacional e gestão do ciclo de vida de aquisições em projetos de pesquisa.

```text
projetos e subsistemas do SisTer
              ↓
     necessidades e recursos
              ↓
        SisTer-Compras
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
git tag -a v0.4.0 -m "release: v0.4.0 - Banco PostgreSQL 17 Dedicado (sister-compras-db:55435), RAG Multi-Turno, Edição update_need e Trava de Persistência"

# Enviar branch principal e tags para o GitHub
git push origin main --tags
```

---

## Recursos da Versão 0.4.0

1. **Banco de Dados PostgreSQL 17 Dedicado e Independente (`sister-compras-db:55435`):**
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
./scripts/run_all.sh dev 8002
```

Acesse a interface web em: **`http://localhost:8002`**

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
