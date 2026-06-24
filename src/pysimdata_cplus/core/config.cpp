#include "pysimdata_cplus/core/config.h"

#include <fstream>
#include <stdexcept>

namespace pysimdata_cplus {

json LoadConfigFile(const std::string& path) {
    std::ifstream file(path);
    if (!file.is_open()) {
        throw std::runtime_error("Failed to open config file: " + path);
    }
    json config;
    file >> config;
    return config;
}

}  // namespace pysimdata_cplus
