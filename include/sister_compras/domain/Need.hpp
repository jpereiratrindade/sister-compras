#ifndef SISTER_COMPRAS_DOMAIN_NEED_HPP
#define SISTER_COMPRAS_DOMAIN_NEED_HPP

#include <string>
#include <vector>
#include "sister_compras/domain/Requirement.hpp"
#include "sister_compras/domain/Alternative.hpp"

namespace sister_compras::domain {

enum class NeedPriority {
    Essential,
    High,
    Medium,
    Low,
    Optional
};

inline std::string priorityToString(NeedPriority priority) {
    switch (priority) {
        case NeedPriority::Essential: return "Essencial";
        case NeedPriority::High: return "Alta";
        case NeedPriority::Medium: return "Media";
        case NeedPriority::Low: return "Baixa";
        case NeedPriority::Optional: return "Opcional";
    }
    return "N/D";
}

enum class NeedStatus {
    Draft,
    Specified,
    InAnalysis,
    Decided,
    Fulfilled,
    Cancelled
};

inline std::string needStatusToString(NeedStatus status) {
    switch (status) {
        case NeedStatus::Draft: return "Rascunho";
        case NeedStatus::Specified: return "Especificada";
        case NeedStatus::InAnalysis: return "Em analise";
        case NeedStatus::Decided: return "Decidida";
        case NeedStatus::Fulfilled: return "Atendida";
        case NeedStatus::Cancelled: return "Cancelada";
    }
    return "Desconhecido";
}

struct Need {
    std::string id;
    std::string project_id;
    std::string title;
    std::string category;
    int quantity{1};
    NeedPriority priority{NeedPriority::Essential};
    NeedStatus status{NeedStatus::Draft};
    std::string deadline;
    std::string responsible;
    std::vector<Requirement> requirements;
    std::vector<Alternative> alternatives;
};

} // namespace sister_compras::domain

#endif // SISTER_COMPRAS_DOMAIN_NEED_HPP
