#include "pysimdata_cplus/generators/bilateral_gaussian.h"

#include <cmath>

namespace pysimdata_cplus {

BilateralGaussian::BilateralGaussian(int rows, int cols, double sigma,
                                     double amplitude, int center_y, int center_x)
    : rows_(rows), cols_(cols), sigma_(sigma), amplitude_(amplitude),
      center_y_(center_y), center_x_(center_x) {
    params_ = {
        {"shape", json::array({rows_, cols_})},
        {"sigma", sigma_},
        {"amplitude", amplitude_},
        {"center", json::array({center_y_, center_x_})}
    };
}

BilateralGaussian::BilateralGaussian(const json& params) {
    auto shape = GetPairParam<int>(params, "shape", {256, 256});
    rows_ = shape.first;
    cols_ = shape.second;
    sigma_ = GetParam<double>(params, "sigma", 10.0);
    amplitude_ = GetParam<double>(params, "amplitude", 255.0);
    auto center = GetPairParam<int>(params, "center", {-1, -1});
    center_y_ = center.first;
    center_x_ = center.second;
    params_ = params;
}

json BilateralGaussian::to_config() const {
    return {
        {"type", "BilateralGaussian"},
        {"format", "csv"},
        {"params", params_}
    };
}

Eigen::MatrixXd BilateralGaussian::do_generate() {
    int cy = (center_y_ < 0) ? rows_ / 2 : center_y_;
    int cx = (center_x_ < 0) ? cols_ / 2 : center_x_;

    Eigen::MatrixXd result(rows_, cols_);
    for (int i = 0; i < rows_; ++i) {
        for (int j = 0; j < cols_; ++j) {
            double dist = std::abs(i - cy) + std::abs(j - cx);
            result(i, j) = amplitude_ * std::exp(-dist / sigma_);
        }
    }
    return result;
}

}  // namespace pysimdata_cplus
