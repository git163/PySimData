#include "pysimdata_cplus/core/generator.h"

#include <algorithm>
#include <chrono>
#include <cctype>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <sstream>
#include <stdexcept>

#include "pysimdata_cplus/generators/gaussian_beam.h"
#include "pysimdata_cplus/generators/gaussian_grid.h"
#include "pysimdata_cplus/generators/function_curve.h"
#include "pysimdata_cplus/generators/erf_curve.h"
#include "pysimdata_cplus/generators/tanh_curve.h"
#include "pysimdata_cplus/generators/cosh_curve.h"
#include "pysimdata_cplus/generators/exponential_decay.h"
#include "pysimdata_cplus/generators/bilateral_gaussian.h"
#include "pysimdata_cplus/io/csv_io.h"
#include "pysimdata_cplus/io/image_io.h"

namespace pysimdata_cplus {

std::unique_ptr<Generator> Generator::from_config(const json& config) {
    if (!config.contains("type")) {
        throw std::runtime_error("Config must contain 'type' field");
    }

    std::string type = config["type"].get<std::string>();
    json params = config.value("params", json::object());

    if (type == "GaussianBeam") {
        return std::make_unique<GaussianBeam>(params);
    } else if (type == "GaussianGrid") {
        return std::make_unique<GaussianGrid>(params);
    } else if (type == "FunctionCurve") {
        return std::make_unique<FunctionCurve>(params);
    } else if (type == "ErfCurve") {
        return std::make_unique<ErfCurve>(params);
    } else if (type == "TanhCurve") {
        return std::make_unique<TanhCurve>(params);
    } else if (type == "CoshCurve") {
        return std::make_unique<CoshCurve>(params);
    } else if (type == "ExponentialDecay") {
        return std::make_unique<ExponentialDecay>(params);
    } else if (type == "BilateralGaussian") {
        return std::make_unique<BilateralGaussian>(params);
    } else {
        throw std::runtime_error("Unknown generator type: " + type);
    }
}

std::unique_ptr<Generator> Generator::from_config_file(const std::string& path) {
    return from_config(LoadConfigFile(path));
}

Eigen::MatrixXd Generator::generate() {
    if (!data_source_.is_null() && !data_source_.empty()) {
        std::string path = data_source_.value("path", "");
        if (path.empty()) {
            throw std::runtime_error("data_source must contain 'path'");
        }
        std::string ext = std::filesystem::path(path).extension().string();
        std::transform(ext.begin(), ext.end(), ext.begin(), ::tolower);

        if (ext == ".csv") {
            data_ = ReadCsv(path, data_source_.value("delimiter", ",").front());
        } else if (ext == ".png" || ext == ".jpg" || ext == ".jpeg" ||
                   ext == ".tif" || ext == ".tiff" || ext == ".bmp") {
            data_ = LoadImage(path);
        } else {
            throw std::runtime_error("Unsupported offline data format: " + ext);
        }
    } else {
        data_ = do_generate();
    }
    return data_;
}

std::string Generator::save(const std::string& output_dir,
                            const std::string& name,
                            bool enable_timestamp) {
    if (data_.size() == 0) {
        throw std::runtime_error("Please call generate() before save()");
    }

    std::string final_dir = output_dir;
    if (enable_timestamp) {
        auto now = std::chrono::system_clock::now();
        auto time = std::chrono::system_clock::to_time_t(now);
        std::stringstream ss;
        ss << std::put_time(std::localtime(&time), "%Y%m%d_%H%M%S");
        final_dir = output_dir + "/" + ss.str();
    }

    std::filesystem::create_directories(final_dir);

    WriteCsv(final_dir + "/" + name + ".csv", data_);
    save_config(final_dir + "/config.json");

    return final_dir;
}

void Generator::save_config(const std::string& path) const {
    std::ofstream file(path);
    if (!file.is_open()) {
        throw std::runtime_error("Failed to open config file for writing: " + path);
    }
    file << to_config().dump(2);
}

void Generator::write_config_file(const std::string& path, const std::string& fmt,
                                  const std::string& data_file) const {
    json config = to_config();
    config["format"] = fmt;  // 覆盖占位 format
    if (!data_file.empty()) {
        config["data_file"] = data_file;
    }
    std::ofstream file(path);
    if (!file.is_open()) {
        throw std::runtime_error("Failed to open config file for writing: " + path);
    }
    file << config.dump(2);
}

std::string Generator::save_all(const std::string& output_dir,
                                const std::string& name,
                                bool timestamped,
                                const std::string& fmt) {
    if (data_.size() == 0) {
        throw std::runtime_error("Please call generate() before save_all()");
    }

    std::string actual_fmt = fmt.empty() ? default_format() : fmt;

    std::string final_dir = output_dir;
    if (timestamped) {
        auto now = std::chrono::system_clock::now();
        auto time = std::chrono::system_clock::to_time_t(now);
        std::stringstream ss;
        ss << std::put_time(std::localtime(&time), "%Y%m%d_%H%M%S");
        final_dir = output_dir + "/" + ss.str();
    }
    std::filesystem::create_directories(final_dir);

    std::string data_file;
    if (actual_fmt == "csv") {
        data_file = name + ".csv";
        WriteCsv(final_dir + "/" + data_file, data_);
    } else if (actual_fmt == "png") {
        data_file = name + ".png";
        SaveImage(final_dir + "/" + data_file, data_, "png");
    } else if (actual_fmt == "tiff" || actual_fmt == "tif") {
        data_file = name + ".tiff";
        SaveImage(final_dir + "/" + data_file, data_, "tiff");
    } else {
        throw std::runtime_error("Unsupported data format for save_all: " + actual_fmt);
    }

    write_config_file(final_dir + "/config.json", actual_fmt, data_file);

    return final_dir;
}

const Eigen::MatrixXd& Generator::data() const {
    if (data_.size() == 0) {
        throw std::runtime_error("Please call generate() before accessing data");
    }
    return data_;
}

const json& Generator::params() const {
    return params_;
}

std::string Generator::default_format() const {
    // 图像类(params 含 shape)默认无损 tiff，其余默认 csv
    if (params_.contains("shape")) {
        return "tiff";
    }
    return "csv";
}

std::pair<int, int> Generator::expected_shape() const {
    // 图像类：直接取 shape
    if (params_.contains("shape") && !params_["shape"].is_null()) {
        auto shape = ToPair<int>(params_["shape"]);
        return {shape.first, shape.second};
    }
    // 曲线类：输出形状为 (y_shape, num_points)
    if (params_.contains("y_shape") && params_.contains("num_points")) {
        return {params_["y_shape"].get<int>(), params_["num_points"].get<int>()};
    }
    // 无法推导，跳过校验
    return {-1, -1};
}

}  // namespace pysimdata_cplus
