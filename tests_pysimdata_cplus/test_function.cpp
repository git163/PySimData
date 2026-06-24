#include "pysimdata_cplus/pysimdata_cplus.h"
#include <gtest/gtest.h>

using namespace pysimdata_cplus;

TEST(FunctionCurve, SinShape) {
    FunctionCurve gen(FunctionCurve::NameToFunc("sin"), 0.0, 6.283185307179586, 50, 1.0, 100);
    auto data = gen.generate();
    EXPECT_EQ(data.rows(), 100);
    EXPECT_EQ(data.cols(), 50);
}

TEST(FunctionCurve, CosShape) {
    FunctionCurve gen(FunctionCurve::NameToFunc("cos"), 0.0, 6.283185307179586, 50, 1.0, 100);
    auto data = gen.generate();
    EXPECT_EQ(data.rows(), 100);
    EXPECT_EQ(data.cols(), 50);
}

TEST(FunctionCurve, ConfigRoundtripPreservesFunc) {
    pysimdata_cplus::json params = {
        {"func", "tan"},
        {"x_range", json::array({0.0, 1.5707963267948966})},
        {"num_points", 25},
        {"amplitude", 1.0},
        {"y_shape", 20}
    };
    FunctionCurve gen(params);
    auto config = gen.to_config();
    EXPECT_EQ(config["params"]["func"].get<std::string>(), "tan");

    auto gen2 = Generator::from_config(config);
    auto data = gen2->generate();
    EXPECT_EQ(data.rows(), 20);
    EXPECT_EQ(data.cols(), 25);
}

TEST(ErfCurve, DefaultShape) {
    ErfCurve gen;
    auto data = gen.generate();
    EXPECT_EQ(data.rows(), 100);
    EXPECT_EQ(data.cols(), 100);
}

TEST(ErfCurve, CustomAmplitude) {
    ErfCurve gen(-1.0, 1.0, 30, 2.0, 10);
    auto data = gen.generate();
    EXPECT_EQ(data.rows(), 10);
    EXPECT_EQ(data.cols(), 30);
}

TEST(TanhCurve, DefaultShape) {
    TanhCurve gen;
    auto data = gen.generate();
    EXPECT_EQ(data.rows(), 100);
    EXPECT_EQ(data.cols(), 100);
}

TEST(CoshCurve, DefaultShape) {
    CoshCurve gen;
    auto data = gen.generate();
    EXPECT_EQ(data.rows(), 100);
    EXPECT_EQ(data.cols(), 100);
}

TEST(CoshCurve, ValuesPositive) {
    CoshCurve gen(-2.0, 2.0, 50, 1.0, 10);
    auto data = gen.generate();
    EXPECT_GT(data.minCoeff(), 0.0);
}
