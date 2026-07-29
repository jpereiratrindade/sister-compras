#ifndef SISTER_COMPRAS_REPOSITORY_I_DATABASE_REPOSITORY_HPP
#define SISTER_COMPRAS_REPOSITORY_I_DATABASE_REPOSITORY_HPP

#include <vector>
#include <optional>
#include <string>
#include "sister_compras/domain/Project.hpp"
#include "sister_compras/domain/Need.hpp"
#include "sister_compras/domain/Decision.hpp"

namespace sister_compras::repository {

class IDatabaseRepository {
public:
    virtual ~IDatabaseRepository() = default;

    virtual bool save(
        const std::vector<domain::Project>& projects,
        const std::vector<domain::Need>& needs,
        const std::vector<domain::Decision>& decisions
    ) = 0;

    virtual bool load(
        std::vector<domain::Project>& out_projects,
        std::vector<domain::Need>& out_needs,
        std::vector<domain::Decision>& out_decisions
    ) = 0;
};

} // namespace sister_compras::repository

#endif // SISTER_COMPRAS_REPOSITORY_I_DATABASE_REPOSITORY_HPP
