#ifndef SISTER_COMPRAS_DOMAIN_PRICE_OBSERVATION_HPP
#define SISTER_COMPRAS_DOMAIN_PRICE_OBSERVATION_HPP

#include <string>

namespace sister_compras::domain {

struct PriceObservation {
    std::string id;
    std::string alternative_id;
    std::string supplier;
    double unit_price{0.0};
    std::string currency{"BRL"};
    std::string observed_date;
    std::string source_url;
    std::string notes;
};

} // namespace sister_compras::domain

#endif // SISTER_COMPRAS_DOMAIN_PRICE_OBSERVATION_HPP
