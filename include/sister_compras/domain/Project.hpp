#ifndef SISTER_COMPRAS_DOMAIN_PROJECT_HPP
#define SISTER_COMPRAS_DOMAIN_PROJECT_HPP

#include <string>
#include <vector>

namespace sister_compras::domain {

struct Project {
    std::string id;
    std::string name;
    std::string description;
    std::string lead_researcher;
    std::vector<std::string> cost_centers;
    std::string start_date;
    std::string end_date;
};

} // namespace sister_compras::domain

#endif // SISTER_COMPRAS_DOMAIN_PROJECT_HPP
