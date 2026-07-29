# Integração candidata com SisTer Nexo

## Estado

Este repositório é candidato à integração federada com o SisTer Nexo. Ele ainda
não é iniciado pelo `SisTer/scripts/run_all.sh`, e **Nexo-Compras** é apenas o
nome de produto em avaliação.

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

## Bloqueios atuais

- `55435` colide com o PostgreSQL de teste do SisTer;
- contrato e aplicação estão em versões diferentes;
- credenciais padrão ainda aparecem no script de execução;
- saúde sanitizada e identidade federada não foram implementadas.

Consulte
[`adr/ADR-005-nexo-compras-federated-boundary.md`](adr/ADR-005-nexo-compras-federated-boundary.md).
