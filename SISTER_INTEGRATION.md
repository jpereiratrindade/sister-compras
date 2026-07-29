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

## Aperto de mãos bilateral

Cada sistema persiste seu próprio `IntegrationAgreement`, correlacionado por
identificador, revisão e digest. O Nexo propõe; o Compras pode aceitar ou
contrapropor capacidades individualmente; o Nexo adota a contraproposta e
ativa a revisão aceita. Suspensão e revogação também produzem recibos nos dois
lados.

O acordo pode ser operado pelas duas interfaces web. Essa interface não
substitui a API: ela comanda o Aggregate local, e os sistemas sincronizam a
decisão por endpoints contratuais. Assim, a governança é humana e visível sem
transformar cliques ou telas em protocolo implícito.

## Metadados de projetos

A capacidade `nexo.project-context.read` transporta o catálogo mínimo
`nexo-project-context/1.0.0`: identificador, nome e estado do projeto, além de
referências de atividades científicas e operacionais. O Compras exibe esses
metadados como referências externas e nunca os trata como registros sob sua
autoridade.

Consulte
[`adr/ADR-005-nexo-compras-federated-boundary.md`](adr/ADR-005-nexo-compras-federated-boundary.md).
