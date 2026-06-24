#ifndef PYSIMDATA_CPLUS_CORE_CONFIG_H_
#define PYSIMDATA_CPLUS_CORE_CONFIG_H_

#include <nlohmann/json.hpp>
#include <string>
#include <vector>

namespace pysimdata_cplus {

using json = nlohmann::json;

// 从文件加载 JSON 配置
json LoadConfigFile(const std::string& path);

// 将 JSON 数组转为指定类型的 std::vector
template <typename T>
std::vector<T> ToVector(const json& value) {
    return value.get<std::vector<T>>();
}

// 将 JSON 数组转为 std::pair（用于 shape、center、x_range 等）
template <typename T>
std::pair<T, T> ToPair(const json& value) {
    auto vec = value.get<std::vector<T>>();
    if (vec.size() != 2) {
        throw std::runtime_error("Expected JSON array of size 2");
    }
    return {vec[0], vec[1]};
}

// 将 std::pair 转为 JSON 数组
template <typename T>
json PairToJson(const std::pair<T, T>& pair) {
    return json::array({pair.first, pair.second});
}

// 从 JSON 对象中获取参数，若不存在则返回默认值
template <typename T>
T GetParam(const json& params, const std::string& key, const T& default_value) {
    if (params.contains(key) && !params[key].is_null()) {
        return params[key].get<T>();
    }
    return default_value;
}

// 从 JSON 对象中获取 pair 参数，若不存在则返回默认值
template <typename T>
std::pair<T, T> GetPairParam(const json& params, const std::string& key,
                              const std::pair<T, T>& default_value) {
    if (params.contains(key) && !params[key].is_null()) {
        return ToPair<T>(params[key]);
    }
    return default_value;
}

}  // namespace pysimdata_cplus

#endif  // PYSIMDATA_CPLUS_CORE_CONFIG_H_
