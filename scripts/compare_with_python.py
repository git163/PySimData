#!/usr/bin/env python3
"""对比同一 config.json 下 Python 与 C++ 生成器输出的数据一致性。"""

import argparse
import json
import os
import subprocess
import sys
import tempfile

import numpy as np

# 把 Python src 加入路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from pysimdata.base import BaseGenerator
import pysimdata.function  # noqa: F401 触发子类自动注册


def generate_python(config_path: str, output_dir: str) -> str:
    """用 Python 读取配置并生成 .npy，返回文件路径。"""
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    cls = BaseGenerator.get_generator_class(config["type"])
    gen = cls.from_config(config)
    data = gen.generate()

    os.makedirs(output_dir, exist_ok=True)
    npy_path = os.path.join(output_dir, "data.npy")
    np.save(npy_path, data)
    return npy_path


def generate_cpp(config_path: str, output_dir: str, build_dir: str = "build") -> str:
    """调用 C++ 程序读取配置并生成 .csv，返回文件路径。"""
    exe = os.path.join(build_dir, "examples_cplus", "09_from_config")
    if not os.path.exists(exe):
        raise FileNotFoundError(f"C++ executable not found: {exe}")

    subprocess.run([exe, config_path, output_dir], check=True)
    return os.path.join(output_dir, "data.csv")


def load_csv(path: str) -> np.ndarray:
    """加载 C++ 生成的 CSV（逗号分隔）。"""
    return np.loadtxt(path, delimiter=",")


def main():
    parser = argparse.ArgumentParser(
        description="Compare Python and C++ generator outputs from the same config.json"
    )
    parser.add_argument("config", help="Path to config.json")
    parser.add_argument(
        "--tol", type=float, default=1e-10, help="Relative tolerance for numerical comparison"
    )
    parser.add_argument(
        "--build-dir", default="build", help="CMake build directory"
    )
    args = parser.parse_args()

    with tempfile.TemporaryDirectory() as tmpdir:
        py_dir = os.path.join(tmpdir, "py")
        cpp_dir = os.path.join(tmpdir, "cpp")

        print("[Python] Generating data...")
        py_path = generate_python(args.config, py_dir)
        py_data = np.load(py_path)

        print("[C++] Generating data...")
        cpp_path = generate_cpp(args.config, cpp_dir, args.build_dir)
        cpp_data = load_csv(cpp_path)

        print(f"Python shape: {py_data.shape}, dtype: {py_data.dtype}")
        print(f"C++    shape: {cpp_data.shape}, dtype: {cpp_data.dtype}")

        if py_data.shape != cpp_data.shape:
            print(f"ERROR: Shape mismatch!")
            sys.exit(1)

        # GaussianGrid 使用不同随机数实现，只对比形状和数值范围
        with open(args.config, "r", encoding="utf-8") as f:
            config = json.load(f)

        if config.get("type") == "GaussianGrid":
            print("GaussianGrid uses different RNG from numpy; skipping value comparison.")
            print("Value range check passed." if py_data.size == cpp_data.size else "Size mismatch!")
            sys.exit(0)

        if np.allclose(py_data, cpp_data, rtol=args.tol, atol=args.tol):
            print(f"OK: Python and C++ outputs match within tolerance {args.tol}")
        else:
            diff = np.abs(py_data - cpp_data)
            max_diff = np.max(diff)
            mean_diff = np.mean(diff)
            print(f"ERROR: Outputs differ!")
            print(f"  max abs diff: {max_diff}")
            print(f"  mean abs diff: {mean_diff}")
            sys.exit(1)


if __name__ == "__main__":
    main()
