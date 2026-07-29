# SisTer-Compras

**SisTer-Compras** é um subsistema federado autônomo do ecossistema **SisTer** desenvolvido em **C++20** para governança de necessidades, especificação de requisitos, cotações, evidências de proveniência, suporte à decisão técnica supervisionada por IA e gestão do ciclo de vida de aquisições em projetos de pesquisa.

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
- **Política de Versionamento:** Semantic Versioning com tags Git anotadas padrão (`v0.1.0`, `v0.2.0`, `v0.3.0`, ...).
- **Versão Atual:** `0.3.0` (definida em `VERSION` e `CMakeLists.txt`).

### Convenção de Tags Git

As tags seguem o padrão anotado Semantic Versioning:

```bash
# Criar tag de release v0.3.0
git tag -a v0.3.0 -m "release: v0.3.0 - Módulo Lista de Compras, Impressão PDF Selecionada e Assistente IA Ollama (qwen2.5:14b)"

# Enviar branch principal e tags para o GitHub
git push origin main --tags
```

---

## Recursos da Versão 0.3.0

1. **Módulo "Lista de Compras" & Gestão Orçamentária:**
   - Visualização consolidada de itens aprovados para aquisição.
   - Cálculo automático do **Orçamento Total do Projeto em R$**.
   - Gestão de status do ciclo de vida: `Especificada` → `Em análise` → `Decidida` → `Adquirida` → `Entregue`.
2. **Gerador de Lista Oficial de Compras (PDF / Impressão Personalizada):**
   - Impressão total ou **filtrada por seleção de checkboxes** (`/api/reports/shopping-list?ids=...`).
   - Documento formatado para departamento de compras com tabela de itens, valores e assinaturas.
3. **Assistente IA Supervisionado com Ollama Local (`qwen2.5:14b`):**
   - **Especificação:** Geração de requisitos técnicos automáticos com base no título do recurso.
   - **Análise & Decisão:** Avaliação de conformidade técnica, mapeamento de lacunas e rascunho de parecer técnico com cópia em 1-clique.

---

## Comando Único de Execução (Full Cycle)

Para compilar o projeto C++20, rodar todos os testes automatizados, validar contratos de governança e subir a **Interface Web** em um único comando:

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
- `domain::Need`: Agregado raiz de necessidade (categoria, quantidade, prioridade, status).
- `domain::Requirement`: Requisitos obrigatorios, desejaveis, regulatorios, de segurança e logistica.
- `domain::Alternative`: Produtos comerciais, serviços, desenvolvimentos internos e aluguéis.
- `domain::Evidence`: Registros de proveniencia, confiança e validação por especialistas.
- `domain::PriceObservation`: Cotaçoes temporais de fornecedores com moeda e URL.
- `domain::Decision`: Decisao formal registrada por pesquisador com justificativa tecnica.

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
