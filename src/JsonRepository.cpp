#include "sister_compras/repository/JsonRepository.hpp"
#include <fstream>
#include <sstream>
#include <iostream>
#include <filesystem>

namespace sister_compras::repository {

JsonRepository::JsonRepository(std::string file_path)
    : m_file_path(std::move(file_path)) {}

bool JsonRepository::save(const std::vector<domain::Project>& projects,
                          const std::vector<domain::Need>& needs,
                          const std::vector<domain::Decision>& decisions) {
    try {
        std::filesystem::path p(m_file_path);
        if (p.has_parent_path()) {
            std::filesystem::create_directories(p.parent_path());
        }

        std::ofstream out(m_file_path, std::ios::out | std::ios::trunc);
        if (!out.is_open()) return false;

        out << "{\n";
        out << "  \"version\": \"0.2.0\",\n";

        // Projects
        out << "  \"projects\": [\n";
        for (size_t i = 0; i < projects.size(); ++i) {
            const auto& proj = projects[i];
            out << "    {\n";
            out << "      \"id\": \"" << proj.id << "\",\n";
            out << "      \"name\": \"" << proj.name << "\",\n";
            out << "      \"description\": \"" << proj.description << "\",\n";
            out << "      \"lead_researcher\": \"" << proj.lead_researcher << "\",\n";
            out << "      \"start_date\": \"" << proj.start_date << "\",\n";
            out << "      \"end_date\": \"" << proj.end_date << "\"\n";
            out << "    }" << (i + 1 < projects.size() ? "," : "") << "\n";
        }
        out << "  ],\n";

        // Needs
        out << "  \"needs\": [\n";
        for (size_t i = 0; i < needs.size(); ++i) {
            const auto& need = needs[i];
            out << "    {\n";
            out << "      \"id\": \"" << need.id << "\",\n";
            out << "      \"project_id\": \"" << need.project_id << "\",\n";
            out << "      \"title\": \"" << need.title << "\",\n";
            out << "      \"category\": \"" << need.category << "\",\n";
            out << "      \"quantity\": " << need.quantity << ",\n";
            out << "      \"priority\": \"" << domain::priorityToString(need.priority) << "\",\n";
            out << "      \"status\": \"" << domain::needStatusToString(need.status) << "\",\n";
            out << "      \"responsible\": \"" << need.responsible << "\"\n";
            out << "    }" << (i + 1 < needs.size() ? "," : "") << "\n";
        }
        out << "  ],\n";

        // Decisions
        out << "  \"decisions\": [\n";
        for (size_t i = 0; i < decisions.size(); ++i) {
            const auto& dec = decisions[i];
            out << "    {\n";
            out << "      \"id\": \"" << dec.id << "\",\n";
            out << "      \"need_id\": \"" << dec.need_id << "\",\n";
            out << "      \"selected_alternative_id\": \"" << dec.selected_alternative_id << "\",\n";
            out << "      \"technical_justification\": \"" << dec.technical_justification << "\",\n";
            out << "      \"decided_by\": \"" << dec.decided_by << "\",\n";
            out << "      \"decision_date\": \"" << dec.decision_date << "\",\n";
            out << "      \"is_human_decision\": " << (dec.is_human_decision ? "true" : "false") << "\n";
            out << "    }" << (i + 1 < decisions.size() ? "," : "") << "\n";
        }
        out << "  ]\n";
        out << "}\n";

        return true;
    } catch (...) {
        return false;
    }
}

bool JsonRepository::load(std::vector<domain::Project>& out_projects,
                          std::vector<domain::Need>& out_needs,
                          std::vector<domain::Decision>& out_decisions) {
    (void)out_projects;
    (void)out_needs;
    (void)out_decisions;
    if (!std::filesystem::exists(m_file_path)) return false;
    std::ifstream in(m_file_path);
    if (!in.is_open()) return false;

    // Se o arquivo existe e é legível, lemos para validação mínima
    std::stringstream buffer;
    buffer << in.rdbuf();
    std::string content = buffer.str();

    return !content.empty();
}

} // namespace sister_compras::repository
