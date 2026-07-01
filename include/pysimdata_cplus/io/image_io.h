#ifndef PYSIMDATA_CPLUS_IO_IMAGE_IO_H_
#define PYSIMDATA_CPLUS_IO_IMAGE_IO_H_

#include <Eigen/Core>
#include <string>

namespace pysimdata_cplus {

// 使用 OpenCV 加载图像为 Eigen::MatrixXd
// 支持 uint8 灰度图与 float32 tiff（按图像深度无损转 double）
Eigen::MatrixXd LoadImage(const std::string& path);

// 将 Eigen::MatrixXd 保存为原始图片
// fmt=="png"：uint8（0-255，有损截断）；fmt=="tiff"/"tif"：float32（无损）
void SaveImage(const std::string& path, const Eigen::MatrixXd& matrix,
               const std::string& fmt);

}  // namespace pysimdata_cplus

#endif  // PYSIMDATA_CPLUS_IO_IMAGE_IO_H_
