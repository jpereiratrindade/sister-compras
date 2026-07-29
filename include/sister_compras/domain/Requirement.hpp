#ifndef SISTER_COMPRAS_DOMAIN_REQUIREMENT_HPP
#define SISTER_COMPRAS_DOMAIN_REQUIREMENT_HPP

#include <string>

namespace sister_compras::domain {

enum class RequirementType {
    Mandatory,
    Desirable,
    Financial,
    Safety,
    Regulatory,
    Logistical,
    Interoperability
};

inline std::string requirementTypeToString(RequirementType type) {
    switch (type) {
        case RequirementType::Mandatory: return "Obrigatório";
        case RequirementType::Desirable: return "Desejável";
        case RequirementType::Financial: return "Financeiro";
        case RequirementType::Safety: return "Segurança";
        case RequirementType::Regulatory: return "Regulatório";
        case RequirementType::Logistical: return "Logístico";
        case RequirementType::Interoperability: return "Interoperabilidade";
    }
    return "Outro";
}

struct Requirement {
    std::string id;
    std::string need_id;
    RequirementType type{RequirementType::Mandatory};
    std::string description;
    std::string constraint_value;
};

} // namespace sister_compras::domain

#endif // SISTER_COMPRAS_DOMAIN_REQUIREMENT_HPP
