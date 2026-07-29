# Integração com SisTer Nexo

## Estado

Este repositório integra-se ao SisTer Nexo com o nome de produto
**Nexo-Compras**. O identificador `sister_compras` permanece estável.

## Descoberta

1. usar `SISTER_HOME`, quando definido;
2. procurar o repositório irmão `SisTer`;
3. consultar `SisTer/config/local_resources.json` antes de reservar recursos.

## Fronteira

O Nexo será autoridade para projetos e atividades. O Compras continuará
autoridade para necessidades, requisitos, alternativas, cotações, decisões
humanas e atendimento, com banco e credenciais próprios.

Nenhuma integração pode compartilhar tabelas ou assumir que um identificador
local existe no outro banco. O intercâmbio deverá usar contrato versionado,
identidade autenticada, proveniência e referências estáveis.

## Operação

- aplicação em `127.0.0.1:8016`;
- PostgreSQL exclusivo em `127.0.0.1:55440`;
- acesso aninhado em `/integrations/nexo/compras/`;
- contrato `nexo-compras.integration/1.0.0`;
- identidade recebida pelos cabeçalhos `X-Sister-*` encaminhados pelo Nexo;
- contexto de projetos consultado pela API do Nexo.

Consulte
[`adr/ADR-005-nexo-compras-federated-boundary.md`](adr/ADR-005-nexo-compras-federated-boundary.md).
