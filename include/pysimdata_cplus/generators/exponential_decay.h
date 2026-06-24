#ifndef PYSIMDATA_CPLUS_GENERATORS_EXPONENTIAL_DECAY_H_
#define PYSIMDATA_CPLUS_GENERATORS_EXPONENTIAL_DECAY_H_

#include "pysimdata_cplus/core/generator.h"

namespace pysimdata_cplus {

class ExponentialDecay : public Generator {
 public:
    ExponentialDecay(int rows = 256, int cols = 256, double tau = 10.0,
                     double amplitude = 255.0, const std::string& direction = "x");
    explicit ExponentialDecay(const json& params);

    json to_config() const override;

 protected:
    Eigen::MatrixXd do_generate() override;

 private:
    int rows_;
    int cols_;
    double tau_;
    double amplitude_;
    std::string direction_;
};

}  // namespace pysimdata_cplus

#endif  // PYSIMDATA_CPLUS_GENERATORS_EXPONENTIAL_DECAY_H_
