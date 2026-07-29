# Tool Contracts

Define contratos executaveis de interacao entre agente e ferramentas.

## Campos obrigatorios
- contract_version
- tool_name
- tool
- description
- allowed_modes
- risk_level
- policy_refs
- human_approval
- preconditions
- required_evidence
- forbidden_actions
- input_schema
- output_schema

## Regras operacionais
- Ferramentas sem contrato valido nao podem ser usadas em modo executavel
- Ferramentas de risco high ou critical exigem aprovacao humana
- Toda ferramenta deve apontar para politicas que justificam seu uso
- Toda ferramenta deve declarar evidencias minimas de auditoria

## Modo operacional
- explore: leitura, analise e planejamento
- safe-change: alteracao controlada com validacao
- restricted: alteracao apenas sob politicas mais rigidas e aprovacao explicita
