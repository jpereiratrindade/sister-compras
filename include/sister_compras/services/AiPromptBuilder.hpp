#ifndef SISTER_COMPRAS_SERVICES_AI_PROMPT_BUILDER_HPP
#define SISTER_COMPRAS_SERVICES_AI_PROMPT_BUILDER_HPP

#include <string>
#include "sister_compras/domain/Need.hpp"

namespace sister_compras::services {

class AiPromptBuilder {
public:
    static std::string buildSystemPrompt();
    static std::string buildAnalysisPrompt(const domain::Need& need);
};

} // namespace sister_compras::services

#endif // SISTER_COMPRAS_SERVICES_AI_PROMPT_BUILDER_HPP
