#ifndef SISTER_COMPRAS_DOMAIN_DECISION_HPP
#define SISTER_COMPRAS_DOMAIN_DECISION_HPP

#include <string>

namespace sister_compras::domain {

struct Decision {
    std::string id;
    std::string need_id;
    std::string selected_alternative_id;
    std::string technical_justification;
    std::string decided_by;
    std::string decision_date; // YYYY-MM-DD
    bool is_human_decision{true};
    std::string ai_assistant_notes; // Sugestões do modelo, se houver
};

} // namespace sister_compras::domain

#endif // SISTER_COMPRAS_DOMAIN_DECISION_HPP
