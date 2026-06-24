#include "pysimdata_cplus/generators/function_curve.h"

#include <cmath>
#include <unordered_map>

namespace pysimdata_cplus {

FunctionCurve::FuncType FunctionCurve::NameToFunc(const std::string& name) {
    static const std::unordered_map<std::string, FuncType> kFuncMap = {
        {"sin", static_cast<double (*)(double)>(std::sin)},
        {"cos", static_cast<double (*)(double)>(std::cos)},
        {"tan", static_cast<double (*)(double)>(std::tan)},
        {"exp", static_cast<double (*)(double)>(std::exp)},
        {"log", static_cast<double (*)(double)>(std::log)},
        {"sqrt", static_cast<double (*)(double)>(std::sqrt)}
    };
    auto it = kFuncMap.find(name);
    if (it != kFuncMap.end()) {
        return it->second;
    }
    return static_cast<double (*)(double)>(std::sin);
}

FunctionCurve::FunctionCurve(FuncType func, double x_min, double x_max,
                             int num_points, double amplitude, int y_shape)
    : func_(func), x_min_(x_min), x_max_(x_max), num_points_(num_points),
      amplitude_(amplitude), y_shape_(y_shape), func_name_("sin") {
    params_ = {
        {"x_range", json::array({x_min_, x_max_})},
        {"num_points", num_points_},
        {"amplitude", amplitude_},
        {"y_shape", y_shape_},
        {"func", func_name_}
    };
}

FunctionCurve::FunctionCurve(const json& params) {
    auto x_range = GetPairParam<double>(params, "x_range", {0.0, 6.283185307179586});
    x_min_ = x_range.first;
    x_max_ = x_range.second;
    num_points_ = GetParam<int>(params, "num_points", 100);
    amplitude_ = GetParam<double>(params, "amplitude", 1.0);
    y_shape_ = GetParam<int>(params, "y_shape", 100);
    func_name_ = GetParam<std::string>(params, "func", "sin");
    func_ = NameToFunc(func_name_);
    params_ = params;
}

json FunctionCurve::to_config() const {
    json config = {
        {"type", "FunctionCurve"},
        {"format", "csv"},
        {"params", params_}
    };
    config["params"]["func"] = func_name_;
    return config;
}

Eigen::MatrixXd FunctionCurve::do_generate() {
    Eigen::MatrixXd result(y_shape_, num_points_);
    for (int j = 0; j < num_points_; ++j) {
        double x = x_min_ + (x_max_ - x_min_) * j / (num_points_ - 1);
        double y = func_(x) * amplitude_;
        for (int i = 0; i < y_shape_; ++i) {
            result(i, j) = y;
        }
    }
    return result;
}

}  // namespace pysimdata_cplus
