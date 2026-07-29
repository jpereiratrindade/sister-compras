#ifndef SISTER_COMPRAS_REPOSITORY_JSON_REPOSITORY_HPP
#define SISTER_COMPRAS_REPOSITORY_JSON_REPOSITORY_HPP

#include <string>
#include <vector>
#include "sister_compras/domain/Project.hpp"
#include "sister_compras/domain/Need.hpp"
#include "sister_compras/domain/Decision.hpp"

namespace sister_compras::repository {

class JsonRepository {
public:
    explicit JsonRepository(std::string file_path = "storage/compras_data.json");

    bool save(const std::vector<domain::Project>& projects,
              const std::vector<domain::Need>& needs,
              const std::vector<domain::Decision>& decisions);

    bool load(std::vector<domain::Project>& out_projects,
              std::vector<domain::Need>& out_needs,
              std::vector<domain::Decision>& out_decisions);

    std::string getFilePath() const { return m_file_path; }

private:
    std::string m_file_path;
};

} // namespace sister_compras::repository

#endif // SISTER_COMPRAS_REPOSITORY_JSON_REPOSITORY_HPP
