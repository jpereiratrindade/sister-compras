# Evidence and Audit Policy

## Objetivo
Garantir rastreabilidade minima para toda saida relevante produzida com apoio de IA.

## Evidencias obrigatorias
- task_id
- human_owner
- operational_mode
- touched_contexts
- tool_name
- contract_ref
- policy_refs_checked
- tests_executed
- approval_decision
- final_status

## Regras
- Nenhuma mudanca relevante deve ser promovida sem evidencias minimas
- Evidencias devem ser registradas de forma estruturada e versionavel
- Ferramentas de risco high ou critical exigem registro explicito de aprovacao
- Revisao humana deve conseguir reconstruir o racional da execucao
