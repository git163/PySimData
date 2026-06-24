#ifndef PYSIMDATA_CPLUS_IO_CSV_IO_H_
#define PYSIMDATA_CPLUS_IO_CSV_IO_H_

#include <Eigen/Core>
#include <string>

namespace pysimdata_cplus {

// 将 Eigen::MatrixXd 写入 CSV 文件
void WriteCsv(const std::string& path, const Eigen::MatrixXd& matrix,
              char delimiter = ',');

// 从 CSV 文件读取 Eigen::MatrixXd
Eigen::MatrixXd ReadCsv(const std::string& path, char delimiter = ',');

}  // namespace pysimdata_cplus

#endif  // PYSIMDATA_CPLUS_IO_CSV_IO_H_
