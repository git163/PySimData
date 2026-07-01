#include "pysimdata_cplus/io/image_io.h"

#include <gtest/gtest.h>

#include <Eigen/Core>
#include <filesystem>

using namespace pysimdata_cplus;

// tiff 以 float32 保存并读回，数值无损（容差 1e-3）
TEST(ImageIo, TiffFloatLossless) {
    Eigen::MatrixXd m(3, 4);
    m << 0.5, -1.25, 3.14, 100.0,
         -0.001, 42.5, 255.0, 0.0,
         7.0, 8.0, 9.0, 10.0;
    std::filesystem::create_directories("output");
    const std::string path = "output/test_io_float.tiff";
    SaveImage(path, m, "tiff");
    Eigen::MatrixXd back = LoadImage(path);
    ASSERT_EQ(back.rows(), 3);
    ASSERT_EQ(back.cols(), 4);
    EXPECT_LT((back - m).cwiseAbs().maxCoeff(), 1e-3);
}

// png 以 uint8 保存并读回，0-255 整数值精确一致
TEST(ImageIo, PngUint8Roundtrip) {
    Eigen::MatrixXd m(2, 3);
    m << 0, 128, 255,
         10, 20, 30;
    std::filesystem::create_directories("output");
    const std::string path = "output/test_io_u8.png";
    SaveImage(path, m, "png");
    Eigen::MatrixXd back = LoadImage(path);
    ASSERT_EQ(back.rows(), 2);
    ASSERT_EQ(back.cols(), 3);
    for (int i = 0; i < 2; ++i) {
        for (int j = 0; j < 3; ++j) {
            EXPECT_DOUBLE_EQ(back(i, j), m(i, j));
        }
    }
}
