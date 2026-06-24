#include "pysimdata_cplus/generators/gaussian_beam.h"

#include <cmath>

namespace pysimdata_cplus {

GaussianBeam::GaussianBeam(int rows, int cols, double sigma, double amplitude,
                           int center_y, int center_x)
    : rows_(rows), cols_(cols), sigma_(sigma), amplitude_(amplitude),
      center_y_(center_y), center_x_(center_x) {
    params_ = {
        {"shape", json::array({rows_, cols_})},
        {"sigma", sigma_},
        {"amplitude", amplitude_},
        {"center", json::array({center_y_, center_x_})}
    };
}

GaussianBeam::GaussianBeam(const json& params) {
    auto shape = GetPairParam<int>(params, "shape", {256, 256});
    rows_ = shape.first;
    cols_ = shape.second;
    sigma_ = GetParam<double>(params, "sigma", 5.0);
    amplitude_ = GetParam<double>(params, "amplitude", 255.0);
    auto center = GetPairParam<int>(params, "center", {-1, -1});
    center_y_ = center.first;
    center_x_ = center.second;
    params_ = params;
}

json GaussianBeam::to_config() const {
    return {
        {"type", "GaussianBeam"},
        {"format", "csv"},
        {"params", params_}
    };
}

Eigen::MatrixXd GaussianBeam::do_generate() {
    int cy = (center_y_ < 0) ? rows_ / 2 : center_y_;
    int cx = (center_x_ < 0) ? cols_ / 2 : center_x_;

    Eigen::MatrixXd result(rows_, cols_);
    for (int i = 0; i < rows_; ++i) {
        for (int j = 0; j < cols_; ++j) {
            double dy = i - cy;
            double dx = j - cx;
            double dist_sq = dy * dy + dx * dx;
            result(i, j) = amplitude_ * std::exp(-dist_sq / (2.0 * sigma_ * sigma_));
        }
    }
    return result;
}

}  // namespace pysimdata_cplus
