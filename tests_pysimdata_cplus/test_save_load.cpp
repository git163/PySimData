#include "pysimdata_cplus/pysimdata_cplus.h"

#include <gtest/gtest.h>

#include <filesystem>
#include <fstream>

using namespace pysimdata_cplus;

static json ReadJson(const std::string& path) {
    std::ifstream f(path);
    json j;
    f >> j;
    return j;
}

// ---- B1: default_format / expected_shape ----

TEST(DefaultFormat, ImageClassTiff) {
    GaussianGrid g(32, 32, 0.0, 1.0, 4, 1);
    EXPECT_EQ(g.default_format(), "tiff");
}

TEST(DefaultFormat, CurveClassCsv) {
    ErfCurve g(-3.0, 3.0, 100, 1.0, 50);
    EXPECT_EQ(g.default_format(), "csv");
}

TEST(ExpectedShape, ImageClass) {
    GaussianGrid g(32, 48, 0.0, 1.0, 4, 1);
    auto s = g.expected_shape();
    EXPECT_EQ(s.first, 32);
    EXPECT_EQ(s.second, 48);
}

TEST(ExpectedShape, CurveClass) {
    ErfCurve g(-3.0, 3.0, 100, 1.0, 50);  // num_points=100, y_shape=50
    auto s = g.expected_shape();
    EXPECT_EQ(s.first, 50);    // y_shape
    EXPECT_EQ(s.second, 100);  // num_points
}

// ---- B2: save_all ----

TEST(SaveAll, ImageDefaultTiff) {
    GaussianGrid g(32, 32, 0.0, 1.0, 4, 1);
    g.generate();
    const std::string dir = "output/test_saveall_grid";
    std::filesystem::remove_all(dir);
    std::string out = g.save_all(dir);
    EXPECT_EQ(out, dir);  // timestamped 默认 false，无子目录
    EXPECT_TRUE(std::filesystem::exists(out + "/data.tiff"));
    json cfg = ReadJson(out + "/config.json");
    EXPECT_EQ(cfg["format"].get<std::string>(), "tiff");
    EXPECT_EQ(cfg["data_file"].get<std::string>(), "data.tiff");
}

TEST(SaveAll, CurveDefaultCsv) {
    ErfCurve g(-3.0, 3.0, 100, 1.0, 50);
    g.generate();
    const std::string dir = "output/test_saveall_erf";
    std::filesystem::remove_all(dir);
    std::string out = g.save_all(dir);
    EXPECT_TRUE(std::filesystem::exists(out + "/data.csv"));
    json cfg = ReadJson(out + "/config.json");
    EXPECT_EQ(cfg["format"].get<std::string>(), "csv");
    EXPECT_EQ(cfg["data_file"].get<std::string>(), "data.csv");
}

TEST(SaveAll, ExplicitPng) {
    GaussianGrid g(16, 16, 0.0, 1.0, 4, 1);
    g.generate();
    const std::string dir = "output/test_saveall_png";
    std::filesystem::remove_all(dir);
    std::string out = g.save_all(dir, "data", false, "png");
    EXPECT_TRUE(std::filesystem::exists(out + "/data.png"));
    json cfg = ReadJson(out + "/config.json");
    EXPECT_EQ(cfg["format"].get<std::string>(), "png");
    EXPECT_EQ(cfg["data_file"].get<std::string>(), "data.png");
}

TEST(SaveAll, NpyRejected) {
    GaussianGrid g(16, 16, 0.0, 1.0, 4, 1);
    g.generate();
    EXPECT_THROW(g.save_all("output/test_saveall_npy", "data", false, "npy"),
                 std::runtime_error);
}
