#include "pysimdata_cplus/io/image_io.h"

#include <opencv2/opencv.hpp>
#include <stdexcept>

namespace pysimdata_cplus {

Eigen::MatrixXd LoadImage(const std::string& path) {
    cv::Mat img = cv::imread(path, cv::IMREAD_GRAYSCALE);
    if (img.empty()) {
        throw std::runtime_error("Failed to load image: " + path);
    }

    Eigen::MatrixXd matrix(img.rows, img.cols);
    for (int i = 0; i < img.rows; ++i) {
        for (int j = 0; j < img.cols; ++j) {
            matrix(i, j) = static_cast<double>(img.at<uchar>(i, j));
        }
    }
    return matrix;
}

}  // namespace pysimdata_cplus
