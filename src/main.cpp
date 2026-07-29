#include <iostream>
#include <string>
#include "sister_compras/App.hpp"
#include "sister_compras/repository/JsonRepository.hpp"

using namespace sister_compras;
using namespace sister_compras::domain;
using namespace sister_compras::repository;

void runDemo(App& app) {
    std::cout << "=== Inicializando Demonstraçao do SisTer-Compras (Subsistema Autonomo) ===\n\n";

    // 1. Criar projeto de pesquisa generico
    Project proj;
    proj.id = "PROJ-PESQUISA-01";
    proj.name = "Projeto de Pesquisa e Desenvolvimento Tecnologico";
    proj.description = "Desenvolvimento de infraestrutura e prototipagem de recursos para ensaios experimentais.";
    proj.lead_researcher = "Pesquisador Responsavel";
    proj.cost_centers = {"CC-PESQUISA-01", "CC-FOMENTO-2026"};
    proj.start_date = "2026-01-01";
    proj.end_date = "2026-12-31";

    app.service().addProject(proj);
    std::cout << "[+] Projeto cadastrado: " << proj.name << "\n";

    // 2. Cadastrar Necessidade de Infraestrutura
    Need need;
    need.id = "NED-001";
    need.project_id = proj.id;
    need.title = "Alimentar unidade computacional por 8h em operacao de campo";
    need.category = "Energia & Infraestrutura";
    need.quantity = 2;
    need.priority = NeedPriority::Essential;
    need.status = NeedStatus::Specified;
    need.deadline = "2026-09-15";
    need.responsible = "Equipe de Infraestrutura";

    // 3. Adicionar Requisitos
    Requirement r1;
    r1.id = "REQ-01";
    r1.need_id = need.id;
    r1.type = RequirementType::Mandatory;
    r1.description = "Capacidade minima de 500Wh com saida DC 12V/24V regulada";
    r1.constraint_value = ">= 500Wh";

    Requirement r2;
    r2.id = "REQ-02";
    r2.need_id = need.id;
    r2.type = RequirementType::Safety;
    r2.description = "Proteçao IP65 contra intemperies e poeira em ambiente externo";
    r2.constraint_value = "IP65";

    need.requirements.push_back(r1);
    need.requirements.push_back(r2);

    // 4. Adicionar Alternativa Comercial
    Alternative alt1;
    alt1.id = "ALT-01";
    alt1.need_id = need.id;
    alt1.title = "PowerStation Portatil LiFePO4 600Wh Rugged";
    alt1.type = AlternativeType::CommercialProduct;
    alt1.supplier_or_source = "Fornecedor Especializado";
    alt1.description = "Bateria de fosfato de ferro-litio em case estanque com inversor integrado.";

    PriceObservation p1;
    p1.id = "PRC-01";
    p1.alternative_id = alt1.id;
    p1.supplier = "Distribuidora de Equipamentos";
    p1.unit_price = 3450.00;
    p1.currency = "BRL";
    p1.observed_date = "2026-07-28";
    p1.source_url = "https://exemplo.invalid/powerstation-600wh";
    alt1.prices.push_back(p1);

    Evidence ev1;
    ev1.field_name = "capacidade_nominal";
    ev1.value = "614 Wh";
    ev1.source_type = "manual_do_fabricante";
    ev1.source_description = "Manual Tecnico v2.1";
    ev1.consulted_at = "2026-07-29";
    ev1.verified_by = "Pesquisador Responsavel";
    ev1.state = VerificationState::Verified;
    alt1.evidences.push_back(ev1);

    need.alternatives.push_back(alt1);
    app.service().addNeed(need);
    std::cout << "[+] Necessidade '" << need.title << "' cadastrada com " 
              << need.requirements.size() << " requisitos e " 
              << need.alternatives.size() << " alternativas.\n\n";

    // 5. Registrar Decisao Humana Auditavel
    Decision dec;
    dec.id = "DEC-001";
    dec.need_id = need.id;
    dec.selected_alternative_id = alt1.id;
    dec.technical_justification = "A alternativa ALT-01 cumpre o requisito mandatorio de 500Wh (possui 614Wh) e apresenta case estanque IP65 adequado ao ambiente de operacao.";
    dec.decided_by = "Pesquisador Responsavel";
    dec.decision_date = "2026-07-29";
    dec.is_human_decision = true;
    dec.ai_assistant_notes = "Assistente SisTer-Compras confirmou conformidade dos requisitos de IP65 e autonomia estimada em 9.2 horas para a carga de 65W.";

    app.service().recordDecision(dec);
    std::cout << "[+] Decisao registrada com sucesso para a necessidade " << need.id << ".\n\n";

    // 6. Salvar Estado em arquivo JSON
    JsonRepository repo("storage/compras_data.json");
    std::vector<Decision> decisions;
    auto decOpt = app.service().getDecisionForNeed(need.id);
    if (decOpt) decisions.push_back(*decOpt);

    if (repo.save(app.service().getProjects(), app.service().getNeedsByProject(proj.id), decisions)) {
        std::cout << "[+] Estado salvo em " << repo.getFilePath() << "\n\n";
    }

    // 7. Imprimir Relatorio Markdown
    std::cout << "=================== RELATORIO GERADO ===================\n";
    std::cout << app.service().exportProjectReportMarkdown(proj.id);
    std::cout << "========================================================\n";
}

int main(int argc, char* argv[]) {
    App app;
    std::cout << app.getVersion() << "\n\n";

    if (argc > 1 && std::string(argv[1]) == "demo") {
        runDemo(app);
    } else {
        std::cout << "Uso do SisTer-Compras CLI:\n";
        std::cout << "  sister_compras demo     Executa a demonstraçao do fluxo completo e salva o estado em storage/compras_data.json\n\n";
        runDemo(app);
    }

    return 0;
}
