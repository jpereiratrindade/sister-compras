# ADR-AGENT-004 - Context Management

## Status
Aceito

## Contexto
O agente nao preserva intencao com confiabilidade sem contexto explicito.

## Decisao
Contexto deve ser explicito, versionado e reintroduzido por tarefa.

## Estrategia
- Uso de prompts estruturados
- Reinicio controlado de contexto
- Modos operacionais explicitos: explore, safe-change, restricted
