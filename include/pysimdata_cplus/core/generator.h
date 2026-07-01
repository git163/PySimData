#ifndef PYSIMDATA_CPLUS_CORE_GENERATOR_H_
#define PYSIMDATA_CPLUS_CORE_GENERATOR_H_

#include <Eigen/Core>
#include <nlohmann/json.hpp>
#include <memory>
#include <string>
#include <utility>

#include "pysimdata_cplus/core/config.h"

namespace pysimdata_cplus {

class Generator {
 public:
    virtual ~Generator() = default;

    // 核心接口
    Eigen::MatrixXd generate();
    virtual json to_config() const = 0;

 protected:
    // 子类实现具体生成逻辑
    virtual Eigen::MatrixXd do_generate() = 0;

 public:
    // 从配置创建生成器
    static std::unique_ptr<Generator> from_config(const json& config);
    static std::unique_ptr<Generator> from_config_file(const std::string& path);

    // 保存数据与配置到目录
    std::string save(const std::string& output_dir,
                     const std::string& name = "data",
                     bool enable_timestamp = true);
    void save_config(const std::string& path) const;

    const Eigen::MatrixXd& data() const;
    const json& params() const;

    // 默认数据格式：图像类(params 含 shape)用无损 tiff，其余用 csv
    std::string default_format() const;
    // 按 params 推导期望形状：有 shape→{H,W}；有 y_shape+num_points→{y_shape,num_points}；
    // 否则 {-1,-1}（表示跳过校验）
    std::pair<int, int> expected_shape() const;

 protected:
    Eigen::MatrixXd data_;
    json params_;
    json data_source_;  // 离线数据源配置
};

}  // namespace pysimdata_cplus

#endif  // PYSIMDATA_CPLUS_CORE_GENERATOR_H_
