#include "pysimdata_cplus/io/image_io.h"

#include <opencv2/opencv.hpp>
#include <cstdint>
#include <stdexcept>
#include <string>

namespace pysimdata_cplus {

Eigen::MatrixXd LoadImage(const std::string& path) {
    cv::Mat img = cv::imread(path, cv::IMREAD_UNCHANGED);
    if (img.empty()) {
        throw std::runtime_error("Failed to load image: " + path);
    }
    // 多通道图转灰度，保证输出为二维矩阵
    if (img.channels() > 1) {
        cv::cvtColor(img, img, cv::COLOR_BGR2GRAY);
    }

    Eigen::MatrixXd matrix(img.rows, img.cols);
    const int depth = img.depth();
    for (int i = 0; i < img.rows; ++i) {
        for (int j = 0; j < img.cols; ++j) {
            switch (depth) {
                case CV_8U:
                    matrix(i, j) = static_cast<double>(img.at<uchar>(i, j));
                    break;
                case CV_16U:
                    matrix(i, j) = static_cast<double>(img.at<uint16_t>(i, j));
                    break;
                case CV_32F:
                    matrix(i, j) = static_cast<double>(img.at<float>(i, j));
                    break;
                case CV_64F:
                    matrix(i, j) = img.at<double>(i, j);
                    break;
                default:
                    throw std::runtime_error(
                        "Unsupported image depth: " + std::to_string(depth));
            }
        }
    }
    return matrix;
}

void SaveImage(const std::string& path, const Eigen::MatrixXd& matrix,
               const std::string& fmt) {
    const int rows = static_cast<int>(matrix.rows());
    const int cols = static_cast<int>(matrix.cols());

    cv::Mat img;
    if (fmt == "tiff" || fmt == "tif") {
        // float32 无损，适合精确仿真数据
        img.create(rows, cols, CV_32F);
        for (int i = 0; i < rows; ++i) {
            for (int j = 0; j < cols; ++j) {
                img.at<float>(i, j) = static_cast<float>(matrix(i, j));
            }
        }
    } else if (fmt == "png") {
        // uint8，适合 0-255 图像数据（超出范围会截断）
        img.create(rows, cols, CV_8U);
        for (int i = 0; i < rows; ++i) {
            for (int j = 0; j < cols; ++j) {
                img.at<uchar>(i, j) = static_cast<uchar>(matrix(i, j));
            }
        }
    } else {
        throw std::runtime_error("Unsupported image format: " + fmt);
    }

    if (!cv::imwrite(path, img)) {
        throw std::runtime_error("Failed to write image: " + path);
    }
}

}  // namespace pysimdata_cplus
