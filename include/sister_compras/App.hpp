#pragma once

#include <string>
#include "sister_compras/services/PurchasingService.hpp"

namespace sister_compras {

class App {
public:
    App();
    services::PurchasingService& service() { return m_service; }
    const services::PurchasingService& service() const { return m_service; }

    std::string getVersion() const;

private:
    services::PurchasingService m_service;
};

} // namespace sister_compras
