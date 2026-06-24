# PySimData C++ 化实施计划

- 日期: 2026-06-25
- 作者: Claude Code
- 状态: 评审中
- 关联: /Users/tshua/respo/Code/PySimData

## 背景

当前 PySimData 是一个纯 Python 仿真数据生成库，核心逻辑基于 `numpy` 数组运算，包含 8 个生成器类与统一的 `BaseGenerator` 基类。用户希望将其 C++ 化，以脱离 Python 运行时依赖，获得更高的执行效率与更广泛的部署能力（如嵌入式、高性能计算场景）。

## 目标

1. 将核心数据生成逻辑从 Python 迁移到 C++17，代码放在 `src/pysimdata_cplus/`。
2. 提供头文件 + 库形式的 C++ 原生 API。
3. 提供 C++ API 与使用示例，通过代码调用生成数据并保存。
4. 保留现有 JSON 配置格式兼容性（`type` + `params`）。
5. 输出格式统一为 `.csv` 数据与 `.json` 配置；C++ 版本不输出预览图。
6. 使用稳定、开源协议友好的第三方库。
7. **不影响现有 Python 代码**：不删除、不修改 `src/pysimdata/`、`tests/pysimdata/`、`examples/*.py`、`pyproject.toml`。`

## 非目标

1. 不保留 Python API / Python 绑定。
2. 不保留任何绘图/预览图功能；C++ API 仅输出数据与配置。
3. 不支持 TIF/TIFF 离线输入（若后续需要可作为可选扩展）。
4. 不追求与 numpy 100% 浮点逐位一致，但要求数值误差在可接受范围内。

## 方案

### 目标形态

**纯 C++ 库**（不附带 CLI）。

- C++ 核心库：代码位于 `src/pysimdata_cplus/`，命名空间 `pysimdata_cplus`，提供与原有生成器对应的类与统一接口。
- 使用方式：通过 C++ API 调用，或编译运行 `examples/` 下的 C++ 示例程序。
- 与 Python 代码共存：原 `src/pysimdata/`、`tests/pysimdata/`、`examples/*.py` 完全保留。

### 技术栈选型

| 用途 | 选型 | 协议 | 理由 |
|------|------|------|------|
| 数组/矩阵运算 | **Eigen 3.4+** | MPL2 | 稳定、头文件优先、C++ 生态事实标准 |
| JSON 解析/生成 | **nlohmann/json** | MIT | 头文件单库、现代 C++、与 Python dict 映射自然 |
| CSV 文件 I/O | 自实现 | 无 | 格式简单，用标准库 `fstream` 即可，无需第三方依赖 |
| 图像 I/O（离线加载/可选预览） | **OpenCV 4.x** | Apache-2.0 | 你已具备环境，支持 PNG/JPG/TIF/BMP，稳定成熟 |
| 随机数 | `<random>` | 标准库 | 无需第三方依赖 |
| 特殊函数 | `<cmath>` | 标准库 | `std::erf`、`std::tanh`、`std::cosh`、`std::exp` 等 |
| 测试框架 | **GoogleTest** | BSD-3 | C++ 单元测试标准 |
| 构建系统 | **CMake 3.16+** | BSD | 跨平台；依赖通过 `scripts/fetch_deps.sh` 预拉取，CMake 只负责链接 |

### 目录结构

```
PySimData/
├── CMakeLists.txt                  # 根构建配置（仅构建 C++ 部分）
├── pyproject.toml                  # 保留，Python 部分不受影响
├── README.md                       # 可同时说明 Python/C++ 用法
├── CLAUDE.md                       # 沿用现有规范
├── docs/
│   ├── plan-template.md
│   └── 2026-06-25-cpp-migration-plan.md   # 本计划
├── src/
│   ├── pysimdata/                  # 原有 Python 代码，保持不变
│   │   ├── __init__.py
│   │   ├── base.py
│   │   └── function/
│   └── pysimdata_cplus/            # 新增 C++ 代码目录
│       ├── core/
│       │   ├── generator.h
│       │   ├── generator.cpp
│       │   ├── config.h
│       │   └── config.cpp
│       ├── generators/
│       │   ├── gaussian_grid.h/.cpp
│       │   ├── gaussian_beam.h/.cpp
│       │   ├── function_curve.h/.cpp
│       │   ├── erf_curve.h/.cpp
│       │   ├── tanh_curve.h/.cpp
│       │   ├── cosh_curve.h/.cpp
│       │   ├── exponential_decay.h/.cpp
│       │   └── bilateral_gaussian.h/.cpp
│       └── io/
│           ├── csv_io.h/.cpp
│           └── image_io.h/.cpp
├── include/pysimdata_cplus/        # 对外头文件
│   ├── pysimdata_cplus.h
│   └── ...
├── tests_pysimdata_cplus/          # C++ 单元测试（避免与 tests/pysimdata 冲突）
│   ├── CMakeLists.txt
│   ├── test_generator.cpp
│   ├── test_config.cpp
│   ├── test_gaussian.cpp
│   └── test_function.cpp
├── examples_cplus/                 # C++ 示例（避免与 examples/*.py 冲突）
│   ├── 01_gaussian_grid.cpp
│   ├── 02_gaussian_beam.cpp
│   └── ...
├── scripts/
│   └── fetch_deps.sh               # 拉取第三方库到 third_party/
└── third_party/                    # 预拉取的第三方库
    ├── eigen/
    ├── json/
    └── googletest/
```

### 关键设计点

#### 1. Generator 基类

```cpp
namespace pysimdata_cplus {

class Generator {
 public:
  virtual ~Generator() = default;

  // 核心接口
  virtual Eigen::MatrixXd generate() = 0;
  virtual nlohmann::json to_config() const = 0;

  // 配置兼容：从 JSON 字典或文件路径创建
  static std::unique_ptr<Generator> from_config(const nlohmann::json& config);
  static std::unique_ptr<Generator> from_config_file(const std::string& path);

  // 通用工具
  void save(const std::string& output_dir,
            const std::string& name = "data",
            bool enable_timestamp = true);
  void save_config(const std::string& path) const;

  const Eigen::MatrixXd& data() const;
  const nlohmann::json& params() const;

 protected:
  Eigen::MatrixXd data_;
  nlohmann::json params_;
};

}  // namespace pysimdata_cplus
```

#### 2. 生成器类映射

| 原 Python 类 | C++ 类 | 关键算法 |
|--------------|--------|----------|
| `GaussianGrid` | `pysimdata_cplus::GaussianGrid` | Eigen 矩阵 + `<random>` |
| `GaussianBeam` | `pysimdata_cplus::GaussianBeam` | `Eigen::MatrixXd::NullaryExpr` 或逐元素循环 |
| `FunctionCurve` | `pysimdata_cplus::FunctionCurve` | 函数指针/enum + `std::sin` 等 |
| `ErfCurve` | `pysimdata_cplus::ErfCurve` | `std::erf` |
| `TanhCurve` | `pysimdata_cplus::TanhCurve` | `std::tanh` |
| `CoshCurve` | `pysimdata_cplus::CoshCurve` | `std::cosh` |
| `ExponentialDecay` | `pysimdata_cplus::ExponentialDecay` | Eigen 逐元素指数 |
| `BilateralGaussian` | `pysimdata_cplus::BilateralGaussian` | L1 距离高斯 |

#### 3. 配置格式兼容

保持与原 Python 项目一致的 JSON 结构：

```json
{
  "type": "GaussianBeam",
  "format": "csv",
  "params": {
    "shape": [256, 256],
    "sigma": 5.0,
    "amplitude": 255.0,
    "center": [128, 128]
  }
}
```

`Generator::from_config` 根据 `"type"` 字段 dispatch 到对应子类构造函数。

#### 4. 数据输出

- `.csv`：通过自实现工具保存 `Eigen::MatrixXd`（逗号分隔，保留足够精度）。
- `.json`：通过 `nlohmann/json` 保存配置。
- 不输出预览图：C++ 版本不包含绘图功能。

## 影响范围

1. **新增**：`src/pysimdata_cplus/` 完整 C++ 源码树、`tests_pysimdata_cplus/` GoogleTest 测试、`examples_cplus/` C++ 示例、CMake 构建。
2. **保留（不改动）**：原有 `src/pysimdata/` Python 源码、`tests/pysimdata/` Python 测试、`examples/*.py`、`pyproject.toml`。
3. **保留并更新**：`docs/` 文档、`CLAUDE.md` 规范、`README.md`（补充 C++ 用法说明）。
4. **pyproject.toml**：保留，Python 部分继续用它构建；C++ 部分用 CMake 构建。
5. **配置兼容性**：现有 JSON 配置文件可在 C++ 示例或用户代码中加载使用。

## 风险与对策

| 风险 | 对策 |
|------|------|
| Eigen 与 numpy 浮点结果不完全一致 | 测试采用相对误差（如 `1e-10`），并在文档中说明 |
| 随机数序列与 numpy 不同 | 使用 `<random>` 的 `std::mt19937_64`，在文档中明确不保证与 numpy 相同，但保证可重复 seed |
| C++ 构建环境差异（macOS/Linux） | 依赖通过 `scripts/fetch_deps.sh` 统一预拉取；CMake 使用本地路径，CI 中验证两个平台 |
| `.npy` 大端/小端或 Fortran/C 顺序问题 | 已改用 CSV，无此问题 |
| TIF 离线输入 | OpenCV 原生支持，无需额外处理 |
| C++ 无绘图功能 | 在文档中说明；用户可导出 `.csv` 后用 Python/matplotlib/其他工具绘图 |

## 替代方案

1. **保留 Python 绑定（pybind11）**：对现有用户最透明，但用户已明确选择纯 C++ 库，故不采用。
2. **使用 xtensor 替代 Eigen**：xtensor 更像 numpy，但生态与稳定性不如 Eigen；本项目计算简单，Eigen 足够且更成熟。
3. **使用 stb_image 替代 OpenCV**：stb_image 更轻量，但你已有 OpenCV 环境，用 OpenCV 可减少依赖种类并支持 TIF。

## 实施步骤

### 阶段 1：基础设施（约 1 轮）

- [ ] 1.1 创建 `CMakeLists.txt`（C++17、ReleaseWithDebInfo；通过 `find_package` 或显式 `third_party/` 路径查找依赖）。
- [ ] 1.2 创建目录结构 `src/pysimdata_cplus/core/`、`src/pysimdata_cplus/generators/`、`src/pysimdata_cplus/io/`、`include/pysimdata_cplus/`、`tests_pysimdata_cplus/`、`examples_cplus/`。
- [ ] 1.3 创建 `scripts/fetch_deps.sh`：提前拉取 Eigen、nlohmann/json、GoogleTest 到 `third_party/`。
- [ ] 1.4 更新 `.gitignore`（排除 `build/`、`cmake-build-*`、`.cache`）。

### 阶段 2：核心框架（约 1 轮）

- [ ] 2.1 实现 `Generator` 基类：`generate()`、`to_config()`、`from_config()`、`save()`、`save_config()`、`data()`。
- [ ] 2.2 实现配置工具 `config.h/.cpp`：参数类型转换（tuple/list/int/float/string）、JSON 文件读写。
- [ ] 2.3 实现 `csv_io.h/.cpp`：Eigen 矩阵与 CSV 文件互转（支持自定义分隔符，默认逗号）。
- [ ] 2.4 实现 `image_io.h/.cpp`：基于 OpenCV `cv::imread` 加载离线图像数据（PNG/JPG/TIF/BMP）。

### 阶段 3：生成器迁移（约 2 轮）

- [ ] 3.1 迁移 `GaussianBeam`。
- [ ] 3.2 迁移 `BilateralGaussian`。
- [ ] 3.3 迁移 `ExponentialDecay`。
- [ ] 3.4 迁移 `GaussianGrid`（注意随机数种子与分布）。
- [ ] 3.5 迁移 `FunctionCurve`（sin/cos/tan/exp/log/sqrt）。
- [ ] 3.6 迁移 `ErfCurve`（`std::erf`）。
- [ ] 3.7 迁移 `TanhCurve`（`std::tanh`）。
- [ ] 3.8 迁移 `CoshCurve`（`std::cosh`）。

### 阶段 4：C++ 示例（约 1 轮）

- [ ] 4.1 将 8 个 Python 示例改写为 C++ 示例程序，展示 `from_config` / 直接构造 / `generate()` / `save()` 用法。

### 阶段 5：测试（约 1 轮）

- [ ] 5.1 编写 `tests/test_generator.cpp`：基类行为、data 属性异常、func/data_source 二选一。
- [ ] 5.2 编写 `tests/test_config.cpp`：所有 8 个类的 `from_config`/`to_config`/roundtrip。
- [ ] 5.3 编写 `tests/test_gaussian.cpp`：形状、中心值、边界。
- [ ] 5.4 编写 `tests/test_function.cpp`：曲线形状、幅度。
- [ ] 5.5 配置 CI（可选但推荐）：GitHub Actions 在 Ubuntu/macOS 上运行 `cmake --build` + `ctest`。

### 阶段 6：文档与清理（约 1 轮）

- [ ] 6.1 重写 `README.md`：C++ 构建、运行示例、运行测试、API 用法。
- [ ] 6.2 （不执行）保留原 Python 源码目录 `src/pysimdata/` 与 Python 测试目录 `tests/pysimdata/`。
- [ ] 6.3 （不执行）保留 `pyproject.toml`，C++ 构建不依赖它。
- [ ] 6.4 将本计划复制到 `docs/2026-06-25-cpp-migration-plan.md`。
- [ ] 6.5 运行完整测试套件，确保通过。

## 测试计划

1. **C++ 单元测试**：覆盖每个生成器的默认参数、自定义参数、配置 roundtrip、数据形状与边界值。
2. **配置兼容性测试**：使用原 Python 项目生成的 JSON 配置文件，在 C++ 代码中加载并验证输出形状一致。
3. **端到端示例测试**：编译并运行每个 `examples/` 程序，验证输出目录包含 `.csv` 与 `.json`。
4. 数值回归测试：选取若干基准点，与 Python 版本计算结果对比，要求相对误差 `< 1e-10`（高斯点阵因随机数差异除外，仅验证形状与范围）。**CSV 加载测试**：验证 C++ 自写 CSV 可被 Python `np.loadtxt` 正确读回。

## 验证

1. 拉取依赖：`bash scripts/fetch_deps.sh`。
2. 构建：`cmake -B build -S . -DCMAKE_BUILD_TYPE=Release && cmake --build build -j`。
3. 单元测试：`cd build && ctest --output-on-failure`。
4. 示例验证：`./build/examples/01_gaussian_grid`。
5. 数值对比（可选）：用原 Python 版本生成基准 CSV，与新 C++ 版本输出用 Python `pandas`/`numpy` 对比。

## 引用

- 项目根目录：`/Users/tshua/respo/Code/PySimData`
- 原设计文档：`docs/2026-06-24-simdata-generator-design.md`
- 原基类实现：`src/pysimdata/base.py`
- 原生成器实现：`src/pysimdata/function/*.py`
- Eigen: https://eigen.tuxfamily.org
- nlohmann/json: https://github.com/nlohmann/json
- OpenCV: https://opencv.org
- GoogleTest: https://github.com/google/googletest
