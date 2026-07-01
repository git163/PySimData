#include "pysimdata_cplus/pysimdata_cplus.h"

#include <gtest/gtest.h>

using namespace pysimdata_cplus;

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
