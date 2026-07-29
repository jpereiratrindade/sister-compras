# ADR-005 — Fronteira federada entre Nexo e Compras

- Estado: aceito e implementado
- Data: 2026-07-29

## Contexto

O SisTer Nexo é o subsistema de gestão de projetos, ações, atividades de
pesquisa, evidências e publicações. O SisTer-Compras organiza as necessidades,
requisitos, alternativas, cotações e decisões de aquisição originadas por esses
projetos.

Há sobreposição no cadastro de projetos, mas não no domínio: o Nexo explica por
que e em qual atividade um recurso é necessário; o Compras explica como a
necessidade foi especificada, comparada, decidida e atendida.

## Proposta

Preparar este produto como contexto especializado ligado ao Nexo. O nome
**Nexo-Compras** é adotado como nome de produto. Repositório e identificador
`sister_compras` são preservados para compatibilidade.

O Nexo será autoridade para `project_id`, `research_activity_id` e
`activity_id`. O Compras será autoridade para `need_id`, requisitos,
alternativas, observações de preço, `decision_id` e atendimento.

A comunicação ocorrerá por contrato e identidade federada. Não haverá acesso
direto às tabelas, credenciais ou volumes do outro subsistema.

## Dados compartilháveis

Do Nexo para Compras:

- identificadores e títulos mínimos do projeto e da atividade;
- finalidade da necessidade;
- sujeito autenticado e papel autorizado.

Do Compras para Nexo:

- identificador e estado resumido da necessidade;
- referência à decisão humana;
- estado de atendimento;
- referências de evidência explicitamente aprovadas.

Fornecedores, cotações detalhadas, documentos comerciais, conversas e auditoria
bruta permanecem no Compras.

## Implementação

- porta `55440` e volume `nexo_compras_dev_pgdata`;
- contrato `nexo-compras.integration/1.0.0`;
- configuração secreta em `.env` não versionado;
- saúde sanitizada em `/api/health`;
- proxy autenticado do Nexo em `/integrations/nexo/compras/`;
- contexto do Nexo consumido por `/api/nexo/context`;
- acordo bilateral persistido e auditável pelo protocolo
  `sister.integration-agreement/1.0.0`;
- negociação de capacidades e recibos operacionalizados nas interfaces web;
- dados operacionais ignorados e exemplo sanitizado versionado.

## Critérios de aceite

1. recursos locais sem colisão e registrados centralmente;
2. contrato alinhado à versão da aplicação;
3. credenciais somente em configuração local não versionada;
4. banco e volume exclusivos;
5. autenticação delegada ao SisTer;
6. testes de contrato Nexo–Compras;
7. migração e rollback validados;
8. decisão explícita sobre o nome `Nexo-Compras`.
