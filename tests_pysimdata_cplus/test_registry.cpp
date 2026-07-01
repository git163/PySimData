#include "pysimdata_cplus/pysimdata_cplus.h"

#include <gtest/gtest.h>

#include <string>
#include <vector>

using namespace pysimdata_cplus;

// 所有图像类可按 type 字符串分派并生成
TEST(Registry, ImageTypesDispatch) {
    std::vector<std::string> types = {"GaussianGrid", "GaussianBeam",
                                      "BilateralGaussian", "ExponentialDecay"};
    for (const auto& t : types) {
        json cfg = {{"type", t}, {"params", {{"shape", {16, 16}}}}};
        auto gen = Generator::from_config(cfg);
        auto data = gen->generate();
        EXPECT_GT(data.size(), 0) << t;
    }
}

// 所有曲线类可按 type 字符串分派并生成
TEST(Registry, CurveTypesDispatch) {
    std::vector<std::string> types = {"FunctionCurve", "ErfCurve",
                                      "TanhCurve", "CoshCurve"};
    for (const auto& t : types) {
        json cfg = {{"type", t}, {"params", {{"num_points", 20}, {"y_shape", 10}}}};
        auto gen = Generator::from_config(cfg);
        auto data = gen->generate();
        EXPECT_GT(data.size(), 0) << t;
    }
}

// 未知 type 抛异常
TEST(Registry, UnknownTypeThrows) {
    json cfg = {{"type", "NotExist"}, {"params", json::object()}};
    EXPECT_THROW(Generator::from_config(cfg), std::runtime_error);
}
