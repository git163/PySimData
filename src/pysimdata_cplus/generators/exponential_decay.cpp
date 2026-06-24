#include "pysimdata_cplus/generators/exponential_decay.h"

#include <cmath>

namespace pysimdata_cplus {

ExponentialDecay::ExponentialDecay(int rows, int cols, double tau,
                                   double amplitude, const std::string& direction)
    : rows_(rows), cols_(cols), tau_(tau), amplitude_(amplitude),
      direction_(direction) {
    params_ = {
        {"shape", json::array({rows_, cols_})},
        {"tau", tau_},
        {"amplitude", amplitude_},
        {"direction", direction_}
    };
}

ExponentialDecay::ExponentialDecay(const json& params) {
    auto shape = GetPairParam<int>(params, "shape", {256, 256});
    rows_ = shape.first;
    cols_ = shape.second;
    tau_ = GetParam<double>(params, "tau", 10.0);
    amplitude_ = GetParam<double>(params, "amplitude", 255.0);
    direction_ = GetParam<std::string>(params, "direction", "x");
    params_ = params;
}

json ExponentialDecay::to_config() const {
    return {
        {"type", "ExponentialDecay"},
        {"format", "csv"},
        {"params", params_}
    };
}

Eigen::MatrixXd ExponentialDecay::do_generate() {
    Eigen::MatrixXd result(rows_, cols_);
    if (direction_ == "x") {
        for (int j = 0; j < cols_; ++j) {
            double value = amplitude_ * std::exp(-j / tau_);
            for (int i = 0; i < rows_; ++i) {
                result(i, j) = value;
            }
        }
    } else {  // "y"
        for (int i = 0; i < rows_; ++i) {
            double value = amplitude_ * std::exp(-i / tau_);
            for (int j = 0; j < cols_; ++j) {
                result(i, j) = value;
            }
        }
    }
    return result;
}

}  // namespace pysimdata_cplus
