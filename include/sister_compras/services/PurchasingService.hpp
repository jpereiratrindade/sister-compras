#ifndef SISTER_COMPRAS_SERVICES_PURCHASING_SERVICE_HPP
#define SISTER_COMPRAS_SERVICES_PURCHASING_SERVICE_HPP

#include <vector>
#include <optional>
#include <string>
#include "sister_compras/domain/Project.hpp"
#include "sister_compras/domain/Need.hpp"
#include "sister_compras/domain/Decision.hpp"

namespace sister_compras::services {

class PurchasingService {
public:
    PurchasingService() = default;

    // Project management
    void addProject(const domain::Project& project);
    std::vector<domain::Project> getProjects() const;
    std::optional<domain::Project> getProjectById(const std::string& id) const;

    // Need management
    void addNeed(const domain::Need& need);
    std::vector<domain::Need> getNeedsByProject(const std::string& project_id) const;
    std::optional<domain::Need> getNeedById(const std::string& need_id) const;

    // Requirement & Alternative additions
    bool addRequirementToNeed(const std::string& need_id, const domain::Requirement& requirement);
    bool addAlternativeToNeed(const std::string& need_id, const domain::Alternative& alternative);
    bool addPriceObservation(const std::string& need_id, const std::string& alternative_id, const domain::PriceObservation& price);
    bool addEvidenceToAlternative(const std::string& need_id, const std::string& alternative_id, const domain::Evidence& evidence);

    // Decision recording & Budget calculation
    bool recordDecision(const domain::Decision& decision);
    std::optional<domain::Decision> getDecisionForNeed(const std::string& need_id) const;
    double calculateTotalBudget(const std::string& project_id) const;

    // Export JSON / Report
    std::string exportProjectReportJson(const std::string& project_id) const;
    std::string exportProjectReportMarkdown(const std::string& project_id) const;

private:
    std::vector<domain::Project> m_projects;
    std::vector<domain::Need> m_needs;
    std::vector<domain::Decision> m_decisions;
};

} // namespace sister_compras::services

#endif // SISTER_COMPRAS_SERVICES_PURCHASING_SERVICE_HPP
