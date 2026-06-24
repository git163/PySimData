#ifndef PYSIMDATA_CPLUS_GENERATORS_GAUSSIAN_BEAM_H_
#define PYSIMDATA_CPLUS_GENERATORS_GAUSSIAN_BEAM_H_

#include "pysimdata_cplus/core/generator.h"

namespace pysimdata_cplus {

class GaussianBeam : public Generator {
 public:
    GaussianBeam(int rows = 256, int cols = 256, double sigma = 5.0,
                 double amplitude = 255.0, int center_y = -1, int center_x = -1);
    explicit GaussianBeam(const json& params);

    json to_config() const override;

 protected:
    Eigen::MatrixXd do_generate() override;

 private:
    int rows_;
    int cols_;
    double sigma_;
    double amplitude_;
    int center_y_;
    int center_x_;
};

}  // namespace pysimdata_cplus

#endif  // PYSIMDATA_CPLUS_GENERATORS_GAUSSIAN_BEAM_H_
