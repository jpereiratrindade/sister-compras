# Integração com SisTer Nexo

## Estado

Este repositório integra-se ao SisTer Nexo com o nome de produto
**Nexo-Compras**. O identificador `sister_compras` permanece estável.

## Descoberta

1. usar `SISTER_HOME`, quando definido;
2. procurar o repositório irmão `SisTer`;
3. consultar `SisTer/config/local_resources.json` antes de reservar recursos.

## Fronteira

O Nexo é a autoridade para projetos e atividades. O Compras continua
autoridade para necessidades, requisitos, alternativas, cotações, decisões
humanas e atendimento, com banco e credenciais próprios.

Por isso, a interface autenticada do Compras apresenta seu acervo operacional
completo por padrão. O projeto é uma referência atribuível a cada necessidade,
e não um pré-filtro capaz de fazer registros locais desaparecerem. A
visualização por projeto é opcional.

Novos projetos são cadastrados exclusivamente pela interface/API do Nexo. Ao
criar uma necessidade, o Compras exige a seleção de um projeto autorizado
recebido por `nexo-project-context/1.0.0`; não existe mais escolha silenciosa do
primeiro projeto. O registro local guarda somente a referência necessária à
chave estrangeira e à operação do domínio de compras.

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

## Autorização por projeto

O perfil global entregue pelo SisTer é contexto de identidade, não autorização
automática. A consulta do acervo local exige identidade federada, mas não
depende da disponibilidade do catálogo do Nexo. Antes de projetar dados para
fora ou executar uma operação associada a projeto, o Compras solicita ao Nexo
uma decisão para:

- a identidade federada corrente;
- `PROJ-RESILIENCIA`, referência canônica sob autoridade do Nexo;
- a permissão `procurement.view` ou `procurement.manage`.

O identificador histórico `PROJ-PESQUISA-01` permanece somente como alias
contratual para rastreabilidade; os registros existentes são migrados para a
referência canônica sem recriar ou apagar dados.

O Nexo exige vínculo externo ativo e atribuição local da identidade no projeto
para a integração. Membros e auditores podem visualizar a projeção no Nexo;
somente coordenação do projeto ou administração local do Nexo pode executar
operações associadas ao projeto no Compras. Curadores de informação processam
a projeção no Nexo, sem receber por isso autoridade para alterar registros no
Compras.

Falha de comunicação com a autoridade resulta em negação por segurança. A
consulta interna Nexo → Compras usada para construir a projeção informacional
é marcada como chamada contratada já autorizada, evitando um ciclo síncrono.

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
