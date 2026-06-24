# pysimdata

Python simulation data processing project with an optional C++ implementation.

## Python (original)

### Requirements

- Python ≥ 3.9
- `venv` (built into Python 3.3+)

### Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install -e ".[dev]"
```

### Run

```bash
python -m pysimdata
# or
python -c "import pysimdata; print(pysimdata.__version__)"
```

### Test

```bash
pytest
```

### Lint / format

```bash
ruff check .
ruff format .
```

## C++ (`pysimdata_cplus`)

位于 `src/pysimdata_cplus/`，与 Python 代码共存，互不干扰。

### Requirements

- CMake ≥ 3.16
- C++17 compiler
- OpenCV 4.x（用于离线图像加载）

### Setup

```bash
# 拉取 Eigen、nlohmann/json、GoogleTest
bash scripts/fetch_deps.sh

# 构建
cmake -B build -S . -DCMAKE_BUILD_TYPE=Release
cmake --build build -j
```

### Run examples

```bash
./build/examples_cplus/01_gaussian_grid
./build/examples_cplus/02_gaussian_beam
# ...
```

### Run all C++ tests and examples

```bash
bash scripts/run_cpp_tests.sh
```

### Manual build & test

```bash
cd build && ctest --output-on-failure
```

### C++ API usage

```cpp
#include "pysimdata_cplus/pysimdata_cplus.h"

int main() {
    pysimdata_cplus::GaussianBeam gen(256, 256, 5.0, 255.0);
    gen.generate();
    gen.save("output", "data", false);  // 生成 data.csv + config.json
    return 0;
}
```

## Project layout

- `docs/` — 设计文档与计划
- `src/pysimdata/` — Python 包源码（保留）
- `src/pysimdata_cplus/` — C++ 库源码
- `include/pysimdata_cplus/` — C++ 对外头文件
- `tests/pysimdata/` — Python 测试（保留）
- `tests_pysimdata_cplus/` — C++ 测试
- `examples/` — Python 示例（保留）
- `examples_cplus/` — C++ 示例
- `scripts/fetch_deps.sh` — C++ 依赖拉取脚本
- `third_party/` — C++ 第三方依赖

## Conventions

See `CLAUDE.md` at the project root.
