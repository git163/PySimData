#include "pysimdata_cplus/generators/erf_curve.h"

#include <cmath>

namespace pysimdata_cplus {

ErfCurve::ErfCurve(double x_min, double x_max, int num_points,
                   double amplitude, int y_shape)
    : x_min_(x_min), x_max_(x_max), num_points_(num_points),
      amplitude_(amplitude), y_shape_(y_shape) {
    params_ = {
        {"x_range", json::array({x_min_, x_max_})},
        {"num_points", num_points_},
        {"amplitude", amplitude_},
        {"y_shape", y_shape_}
    };
}

ErfCurve::ErfCurve(const json& params) {
    auto x_range = GetPairParam<double>(params, "x_range", {-3.0, 3.0});
    x_min_ = x_range.first;
    x_max_ = x_range.second;
    num_points_ = GetParam<int>(params, "num_points", 100);
    amplitude_ = GetParam<double>(params, "amplitude", 1.0);
    y_shape_ = GetParam<int>(params, "y_shape", 100);
    params_ = params;
}

json ErfCurve::to_config() const {
    return {
        {"type", "ErfCurve"},
        {"format", "csv"},
        {"params", params_}
    };
}

Eigen::MatrixXd ErfCurve::do_generate() {
    Eigen::MatrixXd result(y_shape_, num_points_);
    for (int j = 0; j < num_points_; ++j) {
        double x = x_min_ + (x_max_ - x_min_) * j / (num_points_ - 1);
        double y = std::erf(x) * amplitude_;
        for (int i = 0; i < y_shape_; ++i) {
            result(i, j) = y;
        }
    }
    return result;
}

}  // namespace pysimdata_cplus
