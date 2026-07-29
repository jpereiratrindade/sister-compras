#ifndef SISTER_COMPRAS_DOMAIN_EVIDENCE_HPP
#define SISTER_COMPRAS_DOMAIN_EVIDENCE_HPP

#include <string>

namespace sister_compras::domain {

enum class VerificationState {
    Unverified,
    Extracted,
    Verified,
    Rejected
};

inline std::string verificationStateToString(VerificationState state) {
    switch (state) {
        case VerificationState::Unverified: return "Nao verificado";
        case VerificationState::Extracted: return "Extraido automaticamente";
        case VerificationState::Verified: return "Verificado pela equipe";
        case VerificationState::Rejected: return "Rejeitado";
    }
    return "Desconhecido";
}

struct Evidence {
    std::string field_name;
    std::string value;
    std::string source_type; // e.g. "manual_do_fabricante", "cotacao", "teste"
    std::string source_description;
    std::string url;
    std::string consulted_at; // YYYY-MM-DD
    std::string verified_by;
    VerificationState state{VerificationState::Unverified};
};

} // namespace sister_compras::domain

#endif // SISTER_COMPRAS_DOMAIN_EVIDENCE_HPP
