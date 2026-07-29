# SisTer-Compras — proposta inicial de assistente de recursos e aquisições para projetos de pesquisa

**Versão:** 0.2  
**Data:** 29 de julho de 2026  
**Status:** Proposta para discussão técnica  
**Vinculação:** Ecossistema SisTer  
**Nome provisório:** SisTer-Compras

## 1. Síntese da revisão

Esta versão corrige duas premissas da proposta inicial:

1. o **SisTer-Compras é um subsistema vinculado ao SisTer**;
2. o **C++ passa a ser considerado a linguagem principal candidata**, em coerência com a base tecnológica predominante dos demais subsistemas do SisTer.

A proposta é desenvolver um subsistema geral para apoiar a gestão de necessidades, recursos, alternativas, evidências, cotações, decisões, inventário e ciclo de vida de itens utilizados em projetos de pesquisa.

## 2. Contexto

Projetos de pesquisa precisam identificar, especificar, selecionar, adquirir, testar, distribuir, manter, compartilhar, substituir e descartar diferentes tipos de recursos.

Esses recursos podem incluir:

- equipamentos científicos;
- acessórios;
- componentes eletrônicos;
- materiais de consumo;
- ferramentas;
- serviços;
- licenças;
- infraestrutura;
- equipamentos de proteção e segurança;
- recursos computacionais;
- itens específicos de protocolos científicos.

Frequentemente, as informações ficam dispersas em planilhas, mensagens, páginas comerciais, documentos técnicos, processos administrativos e memória individual. Isso dificulta recuperar:

- por que determinado item foi considerado necessário;
- quais requisitos orientaram sua seleção;
- quais fontes sustentaram as especificações;
- quais alternativas foram avaliadas ou rejeitadas;
- quais preços foram observados e quando;
- quais itens foram adquiridos, recebidos, testados ou colocados em uso;
- quem está responsável por cada recurso;
- quando será preciso realizar manutenção, reposição ou substituição;
- qual decisão foi humana e qual conteúdo foi apenas sugerido por um modelo.

## 3. Posição no ecossistema SisTer

### 3.1 Natureza do subsistema

O SisTer-Compras deve ser tratado como um **subsistema transversal do SisTer**.

Ele poderá atender diferentes projetos, equipes, módulos e infraestruturas, sem depender do SisTer-Campo para existir.

```text
projetos e subsistemas do SisTer
              ↓
     necessidades e recursos
              ↓
        SisTer-Compras
              ↓
especificação, evidências, avaliação,
decisão, aquisição e ciclo de vida
```

## 4. Propósito

Desenvolver um subsistema local de apoio à:

- identificação de necessidades;
- especificação de requisitos;
- pesquisa e registro de alternativas;
- comparação de produtos, serviços e fornecedores;
- registro de cotações e preços observados;
- justificativa técnica de seleção;
- preparação de listas de compra;
- composição de kits;
- controle de inventário;
- empréstimo, reserva e movimentação de recursos;
- registro de testes, desempenho, falhas e manutenção;
- planejamento de reposição;
- preservação da proveniência das informações;
- preservação da autoria e responsabilidade das decisões;
- apoio de modelos de linguagem locais à análise.

O SisTer-Compras não substitui os procedimentos institucionais de aquisição. Ele organiza a dimensão técnica, científica e histórica que antecede, acompanha e sucede esses procedimentos.

## 5. Princípios

### 5.1 Necessidade antes do produto

A unidade principal do sistema não deve ser o produto comercial, mas a necessidade do projeto.

```text
necessidade
    ↓
requisitos
    ↓
alternativas
    ↓
evidências
    ↓
avaliação
    ↓
decisão
    ↓
ciclo de vida
```

Quando um produto deixa de existir, o requisito permanece. O item é transitório; a engenharia da decisão é patrimônio do projeto.

### 5.2 Coerência com o ecossistema SisTer

A arquitetura deve considerar:

- manutenção por uma equipe que já trabalha majoritariamente em C++;
- reutilização de bibliotecas, padrões, ferramentas e componentes existentes;
- integração futura com outros subsistemas;
- consistência de compilação, testes, distribuição e observabilidade;
- redução da fragmentação tecnológica sem necessidade comprovada.

### 5.3 Decisão humana

O modelo de linguagem poderá organizar informações, apontar lacunas, sugerir comparações e apoiar justificativas. A decisão permanecerá humana, explícita e auditável.

### 5.4 Rastreabilidade

Toda especificação relevante deverá manter:

- fonte;
- data de consulta;
- método de obtenção;
- estado de verificação;
- responsável pela validação;
- vínculo com a necessidade e a decisão.

### 5.5 Separação epistemológica

O sistema deverá distinguir claramente:

- declaração de fabricante ou fornecedor;
- conteúdo extraído automaticamente;
- inferência computacional;
- sugestão produzida por modelo de linguagem;
- avaliação da equipe;
- resultado de teste;
- decisão formal.

### 5.6 Operação local e acesso controlado à rede

O sistema deverá funcionar localmente, sem conexão contínua obrigatória. O acesso à internet será explícito, controlado, registrável e limitado às fontes necessárias.

### 5.7 Formatos e contratos abertos

Dados e decisões devem ser exportáveis em formatos abertos, como:

- JSON;
- CSV;
- Markdown;
- arquivos de intercâmbio definidos por esquemas versionados.

## 6. Escopo funcional inicial

### 6.1 Projetos

Cada projeto poderá conter:

- identificação;
- responsáveis;
- período;
- atividades;
- campanhas;
- centros de custo ou fontes de recurso;
- categorias de recursos;
- documentos associados;
- regras e limites próprios.

### 6.2 Necessidades

Exemplo:

```yaml
necessidade: Alimentar uma unidade computacional durante oito horas de campo
projeto: SisTer-Campo
categoria: Energia
quantidade: 2
prioridade: Essencial
prazo: Antes do ensaio operacional
responsavel: Equipe de infraestrutura
```

### 6.3 Requisitos

Os requisitos poderão ser:

- obrigatórios;
- desejáveis;
- restritivos;
- experimentais;
- regulatórios;
- logísticos;
- financeiros;
- ambientais;
- de interoperabilidade;
- de manutenção;
- de segurança.

### 6.4 Alternativas

Cada alternativa poderá representar:

- produto;
- componente;
- serviço;
- fornecedor;
- solução desenvolvida internamente;
- recurso já disponível;
- aluguel;
- empréstimo;
- compartilhamento;
- recuperação de equipamento;
- alternativa de não aquisição.

### 6.5 Evidências

Cada valor relevante deverá carregar proveniência.

```json
{
  "campo": "potencia_maxima",
  "valor": "65 W",
  "fonte_tipo": "manual_do_fabricante",
  "fonte": "Documento técnico do produto",
  "url": "https://exemplo.invalid/documento",
  "consultado_em": "2026-07-29",
  "extraido_por": "sistema",
  "confianca": "alta",
  "verificado_por": "equipe",
  "estado": "verificado"
}
```

### 6.6 Preços e cotações

Um preço deve ser tratado como observação temporal, e não como propriedade permanente do produto.

Campos mínimos:

- fornecedor;
- preço observado;
- moeda;
- frete;
- quantidade;
- validade da cotação;
- data e hora da consulta;
- disponibilidade;
- prazo de entrega;
- garantia;
- fonte;
- responsável pela verificação.

### 6.7 Avaliação

A avaliação poderá combinar:

- critérios eliminatórios;
- critérios ponderados;
- justificativa textual;
- risco;
- informação ausente;
- necessidade de teste;
- parecer do modelo;
- parecer da equipe.

### 6.8 Decisão

Estados iniciais sugeridos:

```text
rascunho
em especificação
em pesquisa
em cotação
em análise
selecionado para ensaio
aprovado
rejeitado
adquirido
recebido
em uso
substituído
cancelado
```

### 6.9 Inventário e ciclo de vida

Em etapas posteriores, o subsistema poderá controlar:

- identificador interno ou patrimonial;
- localização;
- responsável atual;
- projeto e kit associados;
- disponibilidade;
- empréstimos e reservas;
- calibração;
- manutenção;
- falhas;
- uso acumulado;
- vida útil estimada;
- reposição;
- descarte ou baixa.

## 7. Papel do modelo de linguagem local

### 7.1 Funções permitidas

O modelo poderá:

- estruturar descrições comerciais;
- extrair especificações candidatas;
- normalizar unidades e terminologia;
- comparar alternativas com requisitos previamente definidos;
- apontar incompatibilidades;
- identificar informação ausente ou contraditória;
- sugerir perguntas ao fornecedor;
- resumir evidências;
- apoiar a redação de justificativas;
- explicar avaliações;
- ajudar a compor kits.

### 7.2 Limites

O modelo não deverá:

- inventar especificações;
- promover inferência a fato verificado;
- alterar requisitos para favorecer um candidato;
- tratar anúncio comercial como documentação técnica suficiente;
- decidir sozinho pela aquisição;
- executar compras;
- ocultar incerteza;
- substituir procedimentos administrativos;
- registrar uma sugestão como decisão humana.

### 7.3 Integração recomendada

A integração com o modelo local deverá ocorrer por contrato explícito, preferencialmente por API HTTP local compatível com o serviço de inferência adotado.

O SisTer-Compras não precisa incorporar internamente toda a pilha do modelo. Ele precisa controlar:

- entrada enviada;
- contexto utilizado;
- modelo e versão;
- parâmetros relevantes;
- saída original;
- saída estruturada;
- validação por esquema;
- aceite, edição ou rejeição humana.

## 8. C++ ou Python?

### 8.1 Reconsideração da decisão inicial

A recomendação anterior priorizava Python por velocidade de prototipagem. Essa análise era razoável para um utilitário isolado, mas subestimava dois fatores:

1. o SisTer-Compras pertence ao ecossistema SisTer;
2. a maioria dos subsistemas e da experiência acumulada da equipe está concentrada em C++.

Quando o horizonte considerado é apenas o MVP, Python tende a ser mais rápido. Quando o horizonte inclui anos de manutenção, integração, testes, empacotamento, revisão de código e compartilhamento de componentes, a linguagem predominante do ecossistema passa a ter peso arquitetural próprio.

### 8.2 Decisão inicial revisada

> **Adotar C++ como linguagem principal candidata do SisTer-Compras, preservando Python como ferramenta auxiliar para experimentação, coleta, análise e prototipagem quando isso reduzir risco ou esforço.**

Esta não é uma defesa de C++ por prestígio, desempenho abstrato ou preferência estética. É uma decisão orientada por:

- coerência tecnológica;
- capacidade real da equipe;
- manutenção compartilhada;
- integração com o SisTer;
- redução da dispersão de linguagens;
- reutilização de infraestrutura existente;
- longevidade esperada do subsistema.

### 8.3 O que C++ oferece neste contexto

Para o SisTer-Compras, C++ pode favorecer:

- integração mais direta com componentes existentes do SisTer;
- reutilização de bibliotecas internas;
- padronização de compilação e testes;
- implantação uniforme;
- compartilhamento do modelo de domínio;
- maior previsibilidade de desempenho e uso de recursos;
- distribuição como serviço ou executável local autônomo;
- redução do número de pilhas principais que a equipe precisa manter.

O benefício central não é tornar a página web mais rápida. É manter o subsistema dentro da capacidade operacional e cultural do projeto.

### 8.4 Custos e riscos reconhecidos

A escolha por C++ também traz custos que devem ser assumidos conscientemente:

- maior verbosidade em integrações web e manipulação de documentos;
- ecossistema menos direto para experimentação com LLMs;
- necessidade de selecionar bibliotecas com cuidado;
- maior custo para mudanças muito frequentes no início;
- risco de investir em infraestrutura antes de validar o fluxo de trabalho;
- parsing de páginas externas potencialmente mais trabalhoso;
- gestão mais cuidadosa de dependências e empacotamento.

Esses riscos não invalidam C++. Eles exigem uma estratégia de desenvolvimento que evite transformar o MVP em uma demonstração de engenharia de infraestrutura.

### 8.5 Papel de Python

Python poderá ser utilizado como linguagem auxiliar para:

- protótipos descartáveis;
- experimentos de interação com LLM;
- scripts de importação e migração;
- coleta exploratória de páginas;
- notebooks de análise;
- geração ou validação de conjuntos de teste;
- tarefas pontuais de ciência de dados;
- comparação de alternativas de implementação.

Esses componentes não devem se tornar silenciosamente o núcleo permanente do produto sem uma decisão arquitetural explícita.

### 8.6 Regra prática

```text
C++:
  produto principal
  domínio
  casos de uso
  persistência
  API
  auditoria
  integração oficial com o SisTer

Python:
  experimentos
  scripts auxiliares
  importação e análise exploratória
  provas de conceito com modelos
  ferramentas de desenvolvimento
```

### 8.7 Critérios para revisar a decisão

A decisão por C++ deverá ser revisada se:

- a equipe não conseguir sustentar uma camada web simples com produtividade aceitável;
- a integração com modelos e documentos se tornar o núcleo dominante do sistema;
- o custo de bibliotecas e adaptações superar claramente o ganho de coerência;
- um protótipo Python demonstrar vantagem estrutural, e não apenas rapidez inicial;
- a arquitetura do SisTer passar a adotar oficialmente uma estratégia multilíngue diferente.

Da mesma forma, qualquer componente Python que se torne permanente deverá ser formalmente reconhecido, testado, versionado e incorporado à governança do ecossistema.

## 9. Arquitetura inicial recomendada

A arquitetura deve ser um **monólito modular local**, evitando microsserviços prematuros.

```text
navegador
   ↓
frontend web leve
   ↓
aplicação SisTer-Compras em C++
   ├── domínio
   ├── casos de uso
   ├── API HTTP
   ├── persistência
   ├── avaliação
   ├── auditoria
   ├── integração com fontes
   ├── integração com LLM local
   └── exportação
   ↓
SQLite
```

Integrações:

```text
SisTer-Compras
   ├── serviço local de LLM por HTTP
   ├── páginas e documentos autorizados
   ├── arquivos JSON/CSV/Markdown
   ├── outros subsistemas do SisTer
   └── scripts Python auxiliares, quando necessários
```

## 10. Estratégia de frontend

O frontend não precisa determinar a linguagem do núcleo.

A primeira versão poderá usar:

- HTML renderizado no servidor;
- CSS simples;
- JavaScript mínimo;
- chamadas HTTP assíncronas apenas onde agregarem valor;
- páginas orientadas ao fluxo de trabalho, não a uma experiência visual complexa.

A prioridade deve ser validar:

- cadastro de necessidade;
- definição de requisitos;
- inclusão de candidatos;
- registro de evidências;
- comparação;
- decisão;
- exportação.

## 11. Tecnologias candidatas

A seleção final deve considerar as bibliotecas e padrões já adotados pelo SisTer. Como categorias técnicas, serão necessários:

- padrão C++ compatível com o ecossistema;
- sistema de build já utilizado pela equipe;
- biblioteca HTTP para servidor e cliente;
- serialização JSON;
- acesso a SQLite;
- templates HTML ou renderização equivalente;
- validação de dados;
- logging estruturado;
- testes unitários e de integração;
- cliente HTTP para integração com LLM e fontes;
- parser HTML e tratamento de documentos, quando necessário.

A decisão sobre bibliotecas específicas deve ser registrada separadamente, após verificar:

- maturidade;
- licença;
- manutenção;
- compatibilidade com a base existente;
- facilidade de empacotamento;
- impacto sobre a superfície de dependências.

## 12. Modelo de domínio inicial

Entidades candidatas:

```text
Project
Need
Requirement
Candidate
Supplier
Source
Evidence
PriceObservation
EvaluationCriterion
Evaluation
Decision
PurchaseList
Kit
Asset
Loan
MaintenanceRecord
User
AuditEvent
LlmInteraction
```

Relações centrais:

```text
Project 1 ── N Need
Need 1 ── N Requirement
Need N ── N Candidate
Candidate 1 ── N Evidence
Candidate 1 ── N PriceObservation
Candidate 1 ── N Evaluation
Need 1 ── N Decision
Kit N ── N Asset
Decision 1 ── N AuditEvent
```

## 13. Módulos sugeridos

```text
src/
├── domain/
│   ├── projects/
│   ├── needs/
│   ├── requirements/
│   ├── candidates/
│   ├── evidence/
│   ├── evaluations/
│   ├── decisions/
│   └── inventory/
├── application/
│   ├── commands/
│   ├── queries/
│   └── services/
├── infrastructure/
│   ├── database/
│   ├── http/
│   ├── web_sources/
│   ├── llm/
│   ├── audit/
│   └── exports/
├── presentation/
│   ├── web/
│   └── api/
└── main.cpp
```

Ferramentas auxiliares:

```text
tools/
├── python/
│   ├── imports/
│   ├── experiments/
│   └── datasets/
└── fixtures/
```

## 14. MVP proposto

A primeira versão deve ser pequena, mas estruturalmente correta.

### 14.1 Funcionalidades mínimas

1. cadastrar projeto;
2. cadastrar necessidade;
3. definir requisitos obrigatórios e desejáveis;
4. cadastrar candidatos manualmente;
5. registrar fontes e evidências;
6. registrar preços observados;
7. comparar candidatos;
8. registrar decisão humana;
9. manter histórico de alterações;
10. exportar relatório em Markdown e dados em JSON ou CSV.

### 14.2 Integração inicial com LLM

Na primeira etapa, o modelo poderá:

- receber dados já cadastrados;
- apontar lacunas;
- produzir comparação estruturada;
- sugerir texto de justificativa;
- devolver saída validada por esquema.

A pesquisa autônoma na internet não deverá fazer parte do primeiro núcleo funcional.

## 15. Fases de evolução

```text
v0.1 — domínio, cadastro e comparação manual
v0.2 — integração controlada com LLM local
v0.3 — registro assistido de fontes e documentos
v0.4 — consulta controlada à internet
v0.5 — composição de kits
v0.6 — inventário, empréstimo e reserva
v0.7 — manutenção, falhas e desempenho
v0.8 — planejamento de reposição e integração ampliada com o SisTer
```

## 16. Riscos principais

### Risco 1 — confundir ferramenta técnica com sistema institucional de compras

**Mitigação:** delimitar claramente que o SisTer-Compras apoia especificação, evidência, avaliação e acompanhamento, sem substituir sistemas administrativos oficiais.

### Risco 2 — construir uma aplicação genérica demais

**Mitigação:** utilizar casos reais, inicialmente CampoNode e MorfoCampo, para validar cada entidade e fluxo.

### Risco 3 — transformar C++ em objetivo do projeto

**Mitigação:** usar C++ como meio de integração e manutenção, não como justificativa para complexidade desnecessária.

### Risco 4 — fragmentar o sistema com scripts permanentes não governados

**Mitigação:** manter Python como ferramenta auxiliar explícita e promover qualquer componente permanente a elemento formal da arquitetura.

### Risco 5 — delegar decisão ao modelo

**Mitigação:** exigir decisão humana, preservar a saída original do modelo e registrar aceite, edição ou rejeição.

### Risco 6 — depender de páginas comerciais instáveis

**Mitigação:** preservar proveniência, datas, documentos e estados de verificação.

## 17. Questões para discussão da equipe

1. O SisTer-Compras será formalmente classificado como subsistema do SisTer?
2. Qual padrão de C++ e qual sistema de build devem ser herdados do ecossistema?
3. Quais bibliotecas já utilizadas no SisTer podem ser reaproveitadas?
4. O frontend será renderizado pelo servidor ou separado?
5. Qual contrato será usado para integração com o modelo local?
6. Quais entidades pertencem ao núcleo e quais devem ficar para fases posteriores?
7. Como representar responsabilidade, autoria e decisão?
8. Como importar os inventários e listas atualmente mantidos em Markdown ou planilhas?
9. Quais procedimentos institucionais precisam apenas ser referenciados, sem serem reproduzidos?
10. Quais casos reais validarão o MVP?

## 18. Decisão arquitetural proposta para discussão

```yaml
decisao: Adotar C++ como linguagem principal candidata do SisTer-Compras
status: Proposta
contexto:
  - subsistema vinculado ao SisTer
  - predominância de C++ nos subsistemas existentes
  - necessidade de manutenção e integração de longo prazo
fundamentos:
  - coerência tecnológica
  - capacidade da equipe
  - reutilização de componentes
  - redução da fragmentação
  - distribuição local uniforme
condicoes:
  - monólito modular
  - frontend simples
  - integração com LLM por contrato HTTP
  - dependências avaliadas explicitamente
  - Python permitido como ferramenta auxiliar governada
revisao:
  - após o primeiro protótipo funcional
  - diante de custo desproporcional de integração web ou documental
  - diante de mudança na estratégia tecnológica do SisTer
```

## 19. Síntese

> **O SisTer-Compras será um subsistema transversal do SisTer para apoiar a especificação, seleção, aquisição, organização e acompanhamento de recursos utilizados em projetos de pesquisa. C++ será adotado como linguagem principal candidata por coerência com o ecossistema e pela manutenção de longo prazo, enquanto Python permanecerá disponível como ferramenta auxiliar para experimentação e tarefas especializadas. A inteligência artificial apoiará a análise, mas requisitos, evidências e decisões continuarão explícitos, rastreáveis e sob responsabilidade humana.**

A proposta deve começar pequena. A ambição pode ser grande, mas o primeiro compromisso é resolver bem um fluxo real, sem criar um ERP científico antes de cadastrar o primeiro cabo USB.
