#include "sister_compras/services/AiPromptBuilder.hpp"
#include <sstream>

namespace sister_compras::services {

std::string AiPromptBuilder::buildSystemPrompt() {
    return "Você é o Assistente de Compras e Aquisições do subsistema SisTer-Compras. "
           "Sua função é apoiar pesquisadores analisando requisitos técnicos, comparando alternativas/cotações de fornecedores, "
           "identificando lacunas de evidências e redigindo uma minuta de justificativa técnica. "
           "REGRA FUNDAMENTAL: Sua análise é uma SUGESTÃO. A decisão final é exclusivamente humana, explícita e auditável.";
}

std::string AiPromptBuilder::buildAnalysisPrompt(const domain::Need& need) {
    std::ostringstream ss;
    ss << "Por favor, analise a seguinte necessidade de pesquisa:\n\n";
    ss << "Título: " << need.title << "\n";
    ss << "Categoria: " << need.category << "\n";
    ss << "Quantidade: " << need.quantity << "\n";
    ss << "Prioridade: " << domain::priorityToString(need.priority) << "\n\n";

    if (!need.requirements.empty()) {
        ss << "Requisitos do Projeto:\n";
        for (const auto& req : need.requirements) {
            ss << "- [" << domain::requirementTypeToString(req.type) << "] " << req.description << "\n";
        }
        ss << "\n";
    }

    if (!need.alternatives.empty()) {
        ss << "Alternativas e Cotações Avaliadas:\n";
        for (const auto& alt : need.alternatives) {
            ss << "- " << alt.title << " (" << alt.supplier_or_source << ")\n";
            for (const auto& pr : alt.prices) {
                ss << "  Preço: R$ " << pr.unit_price << " (" << pr.observed_date << ")\n";
            }
        }
        ss << "\n";
    } else {
        ss << "Nenhuma cotação cadastrada até o momento.\n\n";
    }

    ss << "Tarefas:\n";
    ss << "1. Avalie a conformidade técnica das alternativas aos requisitos.\n";
    ss << "2. Aponte lacunas de informação ou evidências faltantes.\n";
    ss << "3. Redija uma minuta sucinta de justificativa técnica de decisão para o pesquisador responsável.\n";

    return ss.str();
}

} // namespace sister_compras::services
