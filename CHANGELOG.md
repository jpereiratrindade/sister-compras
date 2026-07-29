# CHANGELOG — SisTer-Compras

Todas as alterações notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

---

## [0.4.0] - 2026-07-29

### Adicionado
- **Container PostgreSQL 17 Dedicado e Independente (`sister-compras-db:55435`):** Container Podman/Docker exclusivo rodando PostgreSQL na porta `55435`, isolado e autônomo.
- **Assistente IA Conversacional RAG Multi-Turno (`qwen2.5:14b`):** Retenção e acúmulo contínuo de memória entre turnos de conversa.
- **Ação `update_need` (Edição de Registros Existentes):** Reconhecimento por RAG de itens já existentes no banco de dados e atualização via `POST /api/needs/update` sem duplicação de dados.
- **Parsing Monetário em R$:** Conversão automática de strings como `"80,00"`, `"R$ 80"` para float `80.0` no parâmetro `estimated_budget`.
- **Exibição do Orçamento Estimado em R$:** Cálculo de subtotais previstos com badge `(Estimado)` na Lista de Compras.
- **Trava de Persistência contra Re-seeding:** Impede que a base do usuário seja sobrescrita ao reiniciar o script orquestrador `./scripts/run_all.sh`.

---

## [0.3.0] - 2026-07-28

### Adicionado
- **Módulo "Lista de Compras":** Gestão de entregas e cálculo orçamentário total.
- **Relatório Oficial Impresso (PDF Selecionado):** Exportação em PDF por lote de checkboxes.
- **Assistente Ollama Supervisionado:** Integração inicial com modelo `qwen2.5:14b` para análise de conformidade.

---

## [0.2.0] - 2026-07-27

### Adicionado
- **Persistência Relacional DDL (`db/schema.sql`):** Esquema relacional completo para PostgreSQL.
- **Interface Web de Gestão:** Dashboard responsivo para necessidades, cotações e decisões.

---

## [0.1.0] - 2026-07-26

### Adicionado
- **Núcleo de Domínio em C++20:** Agregados `Project`, `Need`, `Requirement`, `Alternative`, `Evidence`, `PriceObservation` e `Decision`.
- **Contratos JSON Schema Federados:** Validação via `validate_governance_repo.py` e `validate_tool_contracts.py`.
