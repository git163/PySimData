#include "pysimdata_cplus/generators/gaussian_grid.h"

#include <cmath>
#include <random>

namespace pysimdata_cplus {

GaussianGrid::GaussianGrid(int rows, int cols, double mean, double std,
                           int num_points, int seed)
    : rows_(rows), cols_(cols), mean_(mean), std_(std),
      num_points_(num_points), seed_(seed) {
    params_ = {
        {"shape", json::array({rows_, cols_})},
        {"mean", mean_},
        {"std", std_},
        {"num_points", num_points_},
        {"seed", seed_}
    };
}

GaussianGrid::GaussianGrid(const json& params) {
    auto shape = GetPairParam<int>(params, "shape", {256, 256});
    rows_ = shape.first;
    cols_ = shape.second;
    mean_ = GetParam<double>(params, "mean", 0.0);
    std_ = GetParam<double>(params, "std", 1.0);
    num_points_ = GetParam<int>(params, "num_points", 10);
    seed_ = GetParam<int>(params, "seed", -1);
    params_ = params;
}

json GaussianGrid::to_config() const {
    return {
        {"type", "GaussianGrid"},
        {"format", "csv"},
        {"params", params_}
    };
}

Eigen::MatrixXd GaussianGrid::do_generate() {
    int grid_size = static_cast<int>(std::sqrt(num_points_));
    if (grid_size * grid_size < num_points_) {
        grid_size = static_cast<int>(std::ceil(std::sqrt(num_points_)));
    }

    int cell_h = rows_ / grid_size;
    int cell_w = cols_ / grid_size;

    std::mt19937_64 rng(seed_ >= 0 ? static_cast<unsigned long>(seed_) : std::random_device{}());
    std::normal_distribution<double> normal_dist(mean_, std_);
    std::uniform_real_distribution<double> sigma_dist(2.0, 5.0);

    Eigen::MatrixXd result = Eigen::MatrixXd::Zero(rows_, cols_);

    for (int i = 0; i < grid_size; ++i) {
        for (int j = 0; j < grid_size; ++j) {
            if (i * grid_size + j >= num_points_) {
                break;
            }

            double amp = normal_dist(rng);
            double sigma = sigma_dist(rng);

            int cy = i * cell_h + cell_h / 2;
            int cx = j * cell_w + cell_w / 2;

            int y1 = i * cell_h;
            int y2 = std::min((i + 1) * cell_h, rows_);
            int x1 = j * cell_w;
            int x2 = std::min((j + 1) * cell_w, cols_);

            for (int y = y1; y < y2; ++y) {
                for (int x = x1; x < x2; ++x) {
                    double dy = y - cy;
                    double dx = x - cx;
                    double dist_sq = dy * dy + dx * dx;
                    result(y, x) += amp * std::exp(-dist_sq / (2.0 * sigma * sigma));
                }
            }
        }
    }

    return result;
}

}  // namespace pysimdata_cplus
