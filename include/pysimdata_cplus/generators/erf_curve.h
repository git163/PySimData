#ifndef PYSIMDATA_CPLUS_GENERATORS_ERF_CURVE_H_
#define PYSIMDATA_CPLUS_GENERATORS_ERF_CURVE_H_

#include "pysimdata_cplus/core/generator.h"

namespace pysimdata_cplus {

class ErfCurve : public Generator {
 public:
    ErfCurve(double x_min = -3.0, double x_max = 3.0, int num_points = 100,
             double amplitude = 1.0, int y_shape = 100);
    explicit ErfCurve(const json& params);

    json to_config() const override;

 protected:
    Eigen::MatrixXd do_generate() override;

 private:
    double x_min_;
    double x_max_;
    int num_points_;
    double amplitude_;
    int y_shape_;
};

}  // namespace pysimdata_cplus

#endif  // PYSIMDATA_CPLUS_GENERATORS_ERF_CURVE_H_
