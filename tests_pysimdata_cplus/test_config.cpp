#include "pysimdata_cplus/pysimdata_cplus.h"
#include <gtest/gtest.h>
#include <filesystem>

using namespace pysimdata_cplus;

class ConfigRoundtrip : public ::testing::Test {
 protected:
    void RunRoundtrip(Generator* gen1) {
        auto data1 = gen1->generate();
        auto config = gen1->to_config();

        EXPECT_TRUE(config.contains("type"));
        EXPECT_TRUE(config.contains("format"));
        EXPECT_EQ(config["format"].get<std::string>(), "csv");
        EXPECT_TRUE(config.contains("params"));

        auto gen2 = Generator::from_config(config);
        auto data2 = gen2->generate();

        EXPECT_EQ(data1.rows(), data2.rows());
        EXPECT_EQ(data1.cols(), data2.cols());
    }
};

TEST_F(ConfigRoundtrip, GaussianBeam) {
    GaussianBeam gen(64, 64, 5.0, 200.0, 32, 32);
    RunRoundtrip(&gen);
}

TEST_F(ConfigRoundtrip, GaussianGrid) {
    GaussianGrid gen(64, 64, 0.0, 1.0, 4, 42);
    RunRoundtrip(&gen);
}

TEST_F(ConfigRoundtrip, FunctionCurve) {
    FunctionCurve gen(FunctionCurve::NameToFunc("cos"), 0.0, 3.141592653589793, 50, 2.0, 30);
    RunRoundtrip(&gen);
}

TEST_F(ConfigRoundtrip, ErfCurve) {
    ErfCurve gen(-2.0, 2.0, 60, 1.5, 40);
    RunRoundtrip(&gen);
}

TEST_F(ConfigRoundtrip, TanhCurve) {
    TanhCurve gen(-3.0, 3.0, 50, 1.0, 30);
    RunRoundtrip(&gen);
}

TEST_F(ConfigRoundtrip, CoshCurve) {
    CoshCurve gen(-2.0, 2.0, 50, 1.0, 30);
    RunRoundtrip(&gen);
}

TEST_F(ConfigRoundtrip, ExponentialDecay) {
    ExponentialDecay gen(64, 64, 15.0, 200.0, "y");
    RunRoundtrip(&gen);
}

TEST_F(ConfigRoundtrip, BilateralGaussian) {
    BilateralGaussian gen(64, 64, 8.0, 200.0, 32, 32);
    RunRoundtrip(&gen);
}

TEST(ConfigFile, LoadFromFile) {
    std::filesystem::create_directories("output");
    GaussianBeam gen(32, 32, 3.0, 100.0, 16, 16);
    gen.save_config("output/test_config.json");

    auto loaded = Generator::from_config_file("output/test_config.json");
    auto data = loaded->generate();
    EXPECT_EQ(data.rows(), 32);
    EXPECT_EQ(data.cols(), 32);
    EXPECT_DOUBLE_EQ(data(16, 16), 100.0);
}
