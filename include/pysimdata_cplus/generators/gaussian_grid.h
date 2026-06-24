#ifndef PYSIMDATA_CPLUS_GENERATORS_GAUSSIAN_GRID_H_
#define PYSIMDATA_CPLUS_GENERATORS_GAUSSIAN_GRID_H_

#include "pysimdata_cplus/core/generator.h"

namespace pysimdata_cplus {

class GaussianGrid : public Generator {
 public:
    GaussianGrid(int rows = 256, int cols = 256, double mean = 0.0,
                 double std = 1.0, int num_points = 10, int seed = -1);
    explicit GaussianGrid(const json& params);

    json to_config() const override;

 protected:
    Eigen::MatrixXd do_generate() override;

 private:
    int rows_;
    int cols_;
    double mean_;
    double std_;
    int num_points_;
    int seed_;
};

}  // namespace pysimdata_cplus

#endif  // PYSIMDATA_CPLUS_GENERATORS_GAUSSIAN_GRID_H_
