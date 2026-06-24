#include "pysimdata_cplus/io/csv_io.h"

#include <fstream>
#include <iomanip>
#include <sstream>
#include <stdexcept>
#include <vector>

namespace pysimdata_cplus {

void WriteCsv(const std::string& path, const Eigen::MatrixXd& matrix,
              char delimiter) {
    std::ofstream file(path);
    if (!file.is_open()) {
        throw std::runtime_error("Failed to open CSV file for writing: " + path);
    }

    file << std::setprecision(17);
    for (Eigen::Index i = 0; i < matrix.rows(); ++i) {
        for (Eigen::Index j = 0; j < matrix.cols(); ++j) {
            file << matrix(i, j);
            if (j + 1 < matrix.cols()) {
                file << delimiter;
            }
        }
        file << '\n';
    }
}

Eigen::MatrixXd ReadCsv(const std::string& path, char delimiter) {
    std::ifstream file(path);
    if (!file.is_open()) {
        throw std::runtime_error("Failed to open CSV file for reading: " + path);
    }

    std::vector<std::vector<double>> data;
    std::string line;
    while (std::getline(file, line)) {
        if (line.empty()) continue;
        std::vector<double> row;
        std::stringstream ss(line);
        std::string cell;
        while (std::getline(ss, cell, delimiter)) {
            row.push_back(std::stod(cell));
        }
        if (!data.empty() && row.size() != data.front().size()) {
            throw std::runtime_error("Inconsistent row size in CSV file: " + path);
        }
        data.push_back(row);
    }

    if (data.empty()) {
        return Eigen::MatrixXd();
    }

    Eigen::MatrixXd matrix(data.size(), data.front().size());
    for (size_t i = 0; i < data.size(); ++i) {
        for (size_t j = 0; j < data[i].size(); ++j) {
            matrix(i, j) = data[i][j];
        }
    }
    return matrix;
}

}  // namespace pysimdata_cplus
