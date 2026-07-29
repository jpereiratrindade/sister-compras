#ifndef SISTER_COMPRAS_DOMAIN_ALTERNATIVE_HPP
#define SISTER_COMPRAS_DOMAIN_ALTERNATIVE_HPP

#include <string>
#include <vector>
#include "sister_compras/domain/Evidence.hpp"
#include "sister_compras/domain/PriceObservation.hpp"

namespace sister_compras::domain {

enum class AlternativeType {
    CommercialProduct,
    Service,
    InternalDevelopment,
    Rental,
    LoanOrReuse,
    NonAcquisition
};

inline std::string alternativeTypeToString(AlternativeType type) {
    switch (type) {
        case AlternativeType::CommercialProduct: return "Produto Comercial";
        case AlternativeType::Service: return "Servico";
        case AlternativeType::InternalDevelopment: return "Desenvolvimento Interno";
        case AlternativeType::Rental: return "Aluguel";
        case AlternativeType::LoanOrReuse: return "Emprestimo/Reuso";
        case AlternativeType::NonAcquisition: return "Nao aquisicao";
    }
    return "Outro";
}

struct Alternative {
    std::string id;
    std::string need_id;
    std::string title;
    AlternativeType type{AlternativeType::CommercialProduct};
    std::string supplier_or_source;
    std::string description;
    std::vector<Evidence> evidences;
    std::vector<PriceObservation> prices;
};

} // namespace sister_compras::domain

#endif // SISTER_COMPRAS_DOMAIN_ALTERNATIVE_HPP
