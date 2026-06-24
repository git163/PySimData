#ifndef PYSIMDATA_CPLUS_GENERATORS_FUNCTION_CURVE_H_
#define PYSIMDATA_CPLUS_GENERATORS_FUNCTION_CURVE_H_

#include "pysimdata_cplus/core/generator.h"

#include <functional>
#include <string>

namespace pysimdata_cplus {

class FunctionCurve : public Generator {
 public:
    using FuncType = std::function<double(double)>;

    FunctionCurve(FuncType func, double x_min = 0.0, double x_max = 6.283185307179586,
                  int num_points = 100, double amplitude = 1.0, int y_shape = 100);
    explicit FunctionCurve(const json& params);

    json to_config() const override;

    static FuncType NameToFunc(const std::string& name);

 protected:
    Eigen::MatrixXd do_generate() override;

 private:
    FuncType func_;
    double x_min_;
    double x_max_;
    int num_points_;
    double amplitude_;
    int y_shape_;
    std::string func_name_;
};

}  // namespace pysimdata_cplus

#endif  // PYSIMDATA_CPLUS_GENERATORS_FUNCTION_CURVE_H_
