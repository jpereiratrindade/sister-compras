# Context Boundary Policy

## Objetivo
Impedir que agentes tratem contextos institucionais como se fossem apenas tarefas tecnicas.

## Regras
- Todo contexto critico deve declarar owner humano explicito
- Contextos criticos nao podem ser alterados por ferramenta generica sem contrato especifico
- Mudancas que cruzam fronteiras de contexto exigem justificativa e evidencias adicionais
- Politicas, ADRs e artefatos normativos sao tratados como infraestrutura de governanca

## Contextos criticos tipicos
- politicas
- contratos de ferramenta
- regras de aprovacao
- documentos ADR/DDD que definem limites operacionais
