# Approval Matrix

## Regras por tipo de mudanca
- docs: aprovacao humana simples
- config: aprovacao humana simples com diff revisado
- codigo fora de contexto critico: aprovacao humana simples e testes
- codigo em contexto critico: aprovacao humana obrigatoria com politica required_if_core_module
- acao destrutiva: aprovacao humana obrigatoria com politica required_if_destructive

## Evidencias minimas
- task_id
- owner
- tool_name
- approval_policy
- tests_executed
- final_status
