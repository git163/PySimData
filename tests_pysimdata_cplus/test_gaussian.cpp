#include "pysimdata_cplus/pysimdata_cplus.h"
#include <gtest/gtest.h>

using namespace pysimdata_cplus;

TEST(GaussianBeam, DefaultShape) {
    GaussianBeam gen;
    auto data = gen.generate();
    EXPECT_EQ(data.rows(), 256);
    EXPECT_EQ(data.cols(), 256);
}

TEST(GaussianBeam, CustomShape) {
    GaussianBeam gen(128, 128, 10.0, 200.0, 64, 64);
    auto data = gen.generate();
    EXPECT_EQ(data.rows(), 128);
    EXPECT_EQ(data.cols(), 128);
    EXPECT_DOUBLE_EQ(data(64, 64), 200.0);
}

TEST(GaussianBeam, DefaultCenter) {
    GaussianBeam gen(64, 64, 5.0, 255.0);
    auto data = gen.generate();
    EXPECT_DOUBLE_EQ(data(32, 32), 255.0);
}

TEST(GaussianGrid, DefaultShape) {
    GaussianGrid gen;
    auto data = gen.generate();
    EXPECT_EQ(data.rows(), 256);
    EXPECT_EQ(data.cols(), 256);
}

TEST(GaussianGrid, CustomParams) {
    GaussianGrid gen(128, 128, 0.0, 1.0, 5, 42);
    auto data = gen.generate();
    EXPECT_EQ(data.rows(), 128);
    EXPECT_EQ(data.cols(), 128);
}

TEST(GaussianGrid, ReproducibleWithSeed) {
    GaussianGrid gen1(64, 64, 0.0, 1.0, 4, 123);
    GaussianGrid gen2(64, 64, 0.0, 1.0, 4, 123);
    auto data1 = gen1.generate();
    auto data2 = gen2.generate();
    EXPECT_TRUE(data1.isApprox(data2));
}

TEST(BilateralGaussian, DefaultCenter) {
    BilateralGaussian gen(64, 64, 10.0, 255.0);
    auto data = gen.generate();
    EXPECT_DOUBLE_EQ(data(32, 32), 255.0);
}

TEST(BilateralGaussian, CustomCenter) {
    BilateralGaussian gen(64, 64, 8.0, 200.0, 16, 48);
    auto data = gen.generate();
    EXPECT_DOUBLE_EQ(data(16, 48), 200.0);
}

TEST(ExponentialDecay, XDirection) {
    ExponentialDecay gen(32, 32, 10.0, 255.0, "x");
    auto data = gen.generate();
    EXPECT_EQ(data.rows(), 32);
    EXPECT_EQ(data.cols(), 32);
    EXPECT_DOUBLE_EQ(data(0, 0), 255.0);
    EXPECT_LT(data(0, 31), data(0, 0));
}

TEST(ExponentialDecay, YDirection) {
    ExponentialDecay gen(32, 32, 10.0, 255.0, "y");
    auto data = gen.generate();
    EXPECT_DOUBLE_EQ(data(0, 0), 255.0);
    EXPECT_LT(data(31, 0), data(0, 0));
}
