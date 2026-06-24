#!/usr/bin/env bash
# 一键运行所有 C++ 测试与示例

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
BUILD_DIR="$ROOT_DIR/build"

# 颜色输出
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=========================================="
echo "PySimData C++ 测试与示例运行脚本"
echo "=========================================="

# 检查依赖是否已拉取
if [ ! -d "$ROOT_DIR/third_party/eigen" ] || \
   [ ! -d "$ROOT_DIR/third_party/json" ] || \
   [ ! -d "$ROOT_DIR/third_party/googletest" ]; then
    echo -e "${YELLOW}第三方依赖未找到，正在拉取...${NC}"
    bash "$SCRIPT_DIR/fetch_deps.sh"
fi

# 配置并构建
echo ""
echo "[1/3] 配置并构建 C++ 项目..."
rm -rf "$BUILD_DIR"
cmake -B "$BUILD_DIR" -S "$ROOT_DIR" -DCMAKE_BUILD_TYPE=Release
cmake --build "$BUILD_DIR" -j"$(sysctl -n hw.ncpu 2>/dev/null || echo 4)"

# 运行测试
echo ""
echo "[2/3] 运行 C++ 单元测试..."
cd "$BUILD_DIR"
ctest --output-on-failure

# 运行示例
echo ""
echo "[3/3] 运行 C++ 示例..."
cd "$ROOT_DIR"
for example in "$BUILD_DIR"/examples_cplus/[0-9][0-9]_*; do
    if [ -x "$example" ]; then
        name=$(basename "$example")
        echo "  Running $name..."
        if [ "$name" = "09_from_config" ]; then
            "$example" "$ROOT_DIR/examples_cplus/test_config_gaussian_beam.json" "$ROOT_DIR/output/from_config"
        else
            "$example"
        fi
    fi
done

echo ""
echo -e "${GREEN}所有 C++ 测试与示例运行完成。${NC}"
