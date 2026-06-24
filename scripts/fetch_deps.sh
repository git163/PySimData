#!/usr/bin/env bash
# 拉取 C++ 第三方依赖到 third_party/

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
THIRD_PARTY_DIR="$ROOT_DIR/third_party"

mkdir -p "$THIRD_PARTY_DIR"
cd "$THIRD_PARTY_DIR"

# Eigen
echo "Fetching Eigen..."
if [ ! -d "eigen" ]; then
    git clone --depth 1 --branch 3.4.0 https://gitlab.com/libeigen/eigen.git eigen
else
    echo "Eigen already exists, skipping."
fi

# nlohmann/json
echo "Fetching nlohmann/json..."
if [ ! -d "json" ]; then
    git clone --depth 1 --branch v3.11.3 https://github.com/nlohmann/json.git json
else
    echo "nlohmann/json already exists, skipping."
fi

# GoogleTest
echo "Fetching GoogleTest..."
if [ ! -d "googletest" ]; then
    git clone --depth 1 --branch v1.14.0 https://github.com/google/googletest.git googletest
else
    echo "GoogleTest already exists, skipping."
fi

echo "All dependencies fetched to $THIRD_PARTY_DIR"
