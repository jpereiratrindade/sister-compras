#include "sister_compras/services/PurchasingService.hpp"
#include <sstream>
#include <algorithm>
#include <iomanip>

namespace sister_compras::services {

void PurchasingService::addProject(const domain::Project& project) {
    m_projects.push_back(project);
}

std::vector<domain::Project> PurchasingService::getProjects() const {
    return m_projects;
}

std::optional<domain::Project> PurchasingService::getProjectById(const std::string& id) const {
    for (const auto& proj : m_projects) {
        if (proj.id == id) return proj;
    }
    return std::nullopt;
}

void PurchasingService::addNeed(const domain::Need& need) {
    m_needs.push_back(need);
}

std::vector<domain::Need> PurchasingService::getNeedsByProject(const std::string& project_id) const {
    std::vector<domain::Need> result;
    for (const auto& need : m_needs) {
        if (need.project_id == project_id) {
            result.push_back(need);
        }
    }
    return result;
}

std::optional<domain::Need> PurchasingService::getNeedById(const std::string& need_id) const {
    for (const auto& need : m_needs) {
        if (need.id == need_id) return need;
    }
    return std::nullopt;
}

bool PurchasingService::addRequirementToNeed(const std::string& need_id, const domain::Requirement& requirement) {
    for (auto& need : m_needs) {
        if (need.id == need_id) {
            need.requirements.push_back(requirement);
            return true;
        }
    }
    return false;
}

bool PurchasingService::addAlternativeToNeed(const std::string& need_id, const domain::Alternative& alternative) {
    for (auto& need : m_needs) {
        if (need.id == need_id) {
            need.alternatives.push_back(alternative);
            return true;
        }
    }
    return false;
}

bool PurchasingService::addPriceObservation(const std::string& need_id, const std::string& alternative_id, const domain::PriceObservation& price) {
    for (auto& need : m_needs) {
        if (need.id == need_id) {
            for (auto& alt : need.alternatives) {
                if (alt.id == alternative_id) {
                    alt.prices.push_back(price);
                    return true;
                }
            }
        }
    }
    return false;
}

bool PurchasingService::addEvidenceToAlternative(const std::string& need_id, const std::string& alternative_id, const domain::Evidence& evidence) {
    for (auto& need : m_needs) {
        if (need.id == need_id) {
            for (auto& alt : need.alternatives) {
                if (alt.id == alternative_id) {
                    alt.evidences.push_back(evidence);
                    return true;
                }
            }
        }
    }
    return false;
}

bool PurchasingService::recordDecision(const domain::Decision& decision) {
    for (auto& need : m_needs) {
        if (need.id == decision.need_id) {
            need.status = domain::NeedStatus::Decided;
            m_decisions.push_back(decision);
            return true;
        }
    }
    return false;
}

std::optional<domain::Decision> PurchasingService::getDecisionForNeed(const std::string& need_id) const {
    for (const auto& dec : m_decisions) {
        if (dec.need_id == need_id) return dec;
    }
    return std::nullopt;
}

std::string PurchasingService::exportProjectReportJson(const std::string& project_id) const {
    auto projOpt = getProjectById(project_id);
    std::ostringstream ss;
    ss << "{\n";
    ss << "  \"project_id\": \"" << project_id << "\",\n";
    if (projOpt) {
        ss << "  \"project_name\": \"" << projOpt->name << "\",\n";
        ss << "  \"lead_researcher\": \"" << projOpt->lead_researcher << "\",\n";
    }
    ss << "  \"needs\": [\n";

    auto needs = getNeedsByProject(project_id);
    for (size_t i = 0; i < needs.size(); ++i) {
        const auto& need = needs[i];
        ss << "    {\n";
        ss << "      \"id\": \"" << need.id << "\",\n";
        ss << "      \"title\": \"" << need.title << "\",\n";
        ss << "      \"category\": \"" << need.category << "\",\n";
        ss << "      \"quantity\": " << need.quantity << ",\n";
        ss << "      \"priority\": \"" << domain::priorityToString(need.priority) << "\",\n";
        ss << "      \"status\": \"" << domain::needStatusToString(need.status) << "\",\n";
        ss << "      \"requirements_count\": " << need.requirements.size() << ",\n";
        ss << "      \"alternatives_count\": " << need.alternatives.size() << "\n";
        ss << "    }" << (i + 1 < needs.size() ? "," : "") << "\n";
    }

    ss << "  ]\n";
    ss << "}\n";
    return ss.str();
}

std::string PurchasingService::exportProjectReportMarkdown(const std::string& project_id) const {
    auto projOpt = getProjectById(project_id);
    std::ostringstream ss;
    ss << "# Relatorio de Necessidades e Decisões de Aquisiçao\n\n";
    if (projOpt) {
        ss << "**Projeto:** " << projOpt->name << " (" << projOpt->id << ")\n";
        ss << "**Responsavel:** " << projOpt->lead_researcher << "\n\n";
    } else {
        ss << "**Projeto ID:** " << project_id << "\n\n";
    }

    auto needs = getNeedsByProject(project_id);
    if (needs.empty()) {
        ss << "*Nenhuma necessidade registrada para este projeto.*\n";
        return ss.str();
    }

    for (const auto& need : needs) {
        ss << "## Necessidade: " << need.title << " [" << need.id << "]\n\n";
        ss << "- **Categoria:** " << need.category << "\n";
        ss << "- **Quantidade:** " << need.quantity << "\n";
        ss << "- **Prioridade:** " << domain::priorityToString(need.priority) << "\n";
        ss << "- **Status:** " << domain::needStatusToString(need.status) << "\n";
        ss << "- **Responsavel:** " << need.responsible << "\n\n";

        if (!need.requirements.empty()) {
            ss << "### Requisitos:\n";
            for (const auto& req : need.requirements) {
                ss << "- **[" << domain::requirementTypeToString(req.type) << "]** " 
                   << req.description;
                if (!req.constraint_value.empty()) {
                    ss << " (Restricao: " << req.constraint_value << ")";
                }
                ss << "\n";
            }
            ss << "\n";
        }

        if (!need.alternatives.empty()) {
            ss << "### Alternativas Avaliadas:\n";
            for (const auto& alt : need.alternatives) {
                ss << "#### " << alt.title << " (" << domain::alternativeTypeToString(alt.type) << ")\n";
                ss << "- **Fonte/Fornecedor:** " << alt.supplier_or_source << "\n";
                ss << "- **Descricao:** " << alt.description << "\n";

                if (!alt.prices.empty()) {
                    ss << "- **Cotaçoes:**\n";
                    for (const auto& pr : alt.prices) {
                        ss << "  - " << pr.supplier << ": " << std::fixed << std::setprecision(2) 
                           << pr.unit_price << " " << pr.currency << " (" << pr.observed_date << ")\n";
                    }
                }
                if (!alt.evidences.empty()) {
                    ss << "- **Evidencias & Proveniencia:**\n";
                    for (const auto& ev : alt.evidences) {
                        ss << "  - " << ev.field_name << " = " << ev.value 
                           << " [" << domain::verificationStateToString(ev.state) << "]\n";
                    }
                }
                ss << "\n";
            }
        }

        auto decOpt = getDecisionForNeed(need.id);
        if (decOpt) {
            ss << "> **DECISAO REGISTRADA:**\n";
            ss << "> - **Alternativa Selecionada:** " << decOpt->selected_alternative_id << "\n";
            ss << "> - **Justificativa Tecnica:** " << decOpt->technical_justification << "\n";
            ss << "> - **Decidido por:** " << decOpt->decided_by << " em " << decOpt->decision_date << "\n\n";
        } else {
            ss << "*Pendente de decisao humana formal.*\n\n";
        }
        ss << "---\n\n";
    }

    return ss.str();
}

} // namespace sister_compras::services
