#include <cstdlib>
#include <iostream>
#include <cassert>
#include "sister_compras/App.hpp"
#include "sister_compras/repository/JsonRepository.hpp"

using namespace sister_compras;
using namespace sister_compras::domain;
using namespace sister_compras::repository;

namespace {

void require(bool condition, const char* message) {
    if (!condition) {
        std::cerr << "FAIL: " << message << "\n";
        std::exit(1);
    }
}

} // namespace

int main() {
    App app;
    require(!app.getVersion().empty(), "Version should not be empty");

    // Test 1: Project creation & lookup
    Project proj;
    proj.id = "P-TEST-01";
    proj.name = "Test Research Project";
    proj.lead_researcher = "Researcher Test";
    app.service().addProject(proj);

    auto retrievedProj = app.service().getProjectById("P-TEST-01");
    require(retrievedProj.has_value(), "Project should be retrieved by ID");
    require(retrievedProj->name == "Test Research Project", "Project name must match");

    // Test 2: Need & Requirement addition
    Need need;
    need.id = "N-TEST-01";
    need.project_id = "P-TEST-01";
    need.title = "High Precision GPS Antenna";
    need.category = "Hardware";
    need.priority = NeedPriority::Essential;
    app.service().addNeed(need);

    Requirement req;
    req.id = "R-01";
    req.need_id = "N-TEST-01";
    req.type = RequirementType::Mandatory;
    req.description = "Multi-band GNSS L1/L2";
    require(app.service().addRequirementToNeed("N-TEST-01", req), "Requirement should be added to need");

    // Test 3: Alternative, Price & Evidence
    Alternative alt;
    alt.id = "ALT-01";
    alt.need_id = "N-TEST-01";
    alt.title = "Helical GNSS Antenna Model X";
    alt.type = AlternativeType::CommercialProduct;
    alt.supplier_or_source = "GNSS Systems Ltd";
    require(app.service().addAlternativeToNeed("N-TEST-01", alt), "Alternative should be added");

    PriceObservation price;
    price.id = "PRC-01";
    price.alternative_id = "ALT-01";
    price.supplier = "GNSS Systems Ltd";
    price.unit_price = 1250.00;
    price.currency = "BRL";
    price.observed_date = "2026-07-29";
    require(app.service().addPriceObservation("N-TEST-01", "ALT-01", price), "Price observation should be added");

    Evidence ev;
    ev.field_name = "frequencias_suportadas";
    ev.value = "GPS L1/L2, GLONASS G1/G2";
    ev.source_type = "datasheet";
    ev.state = VerificationState::Verified;
    require(app.service().addEvidenceToAlternative("N-TEST-01", "ALT-01", ev), "Evidence should be added");

    // Test 4: Decision recording
    Decision dec;
    dec.id = "DEC-01";
    dec.need_id = "N-TEST-01";
    dec.selected_alternative_id = "ALT-01";
    dec.technical_justification = "Frequencias L1/L2 verificadas no datasheet e preco dentro do orçamentario.";
    dec.decided_by = "Researcher Test";
    dec.decision_date = "2026-07-29";
    dec.is_human_decision = true;
    require(app.service().recordDecision(dec), "Decision should be recorded");

    auto retrievedDec = app.service().getDecisionForNeed("N-TEST-01");
    require(retrievedDec.has_value(), "Decision should be retrievable");
    require(retrievedDec->selected_alternative_id == "ALT-01", "Selected alternative ID must match");

    // Test 5: JsonRepository Save & Load Test
    JsonRepository repo("build/test_storage.json");
    std::vector<Decision> decList = {dec};
    require(repo.save(app.service().getProjects(), app.service().getNeedsByProject("P-TEST-01"), decList), "JsonRepository save should succeed");

    std::vector<Project> loadedProjects;
    std::vector<Need> loadedNeeds;
    std::vector<Decision> loadedDecisions;
    require(repo.load(loadedProjects, loadedNeeds, loadedDecisions), "JsonRepository load should succeed");

    // Test 6: Reports export
    std::string jsonReport = app.service().exportProjectReportJson("P-TEST-01");
    require(!jsonReport.empty(), "JSON report should not be empty");

    std::string mdReport = app.service().exportProjectReportMarkdown("P-TEST-01");
    require(!mdReport.empty(), "Markdown report should not be empty");

    std::cout << "All SisTer-Compras unit tests (including JsonRepository) passed successfully!\n";
    return 0;
}
