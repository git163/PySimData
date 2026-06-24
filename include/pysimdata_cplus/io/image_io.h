#ifndef PYSIMDATA_CPLUS_IO_IMAGE_IO_H_
#define PYSIMDATA_CPLUS_IO_IMAGE_IO_H_

#include <Eigen/Core>
#include <string>

namespace pysimdata_cplus {

// 使用 OpenCV 加载图像为灰度 Eigen::MatrixXd
Eigen::MatrixXd LoadImage(const std::string& path);

}  // namespace pysimdata_cplus

#endif  // PYSIMDATA_CPLUS_IO_IMAGE_IO_H_
