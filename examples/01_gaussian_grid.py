"""Example 1: 高斯点阵仿真"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
from pysimdata.function import GaussianGrid


def main():
    gen = GaussianGrid(shape=(128, 128), mean=0, std=1, num_points=5, seed=42)
    data = gen.generate()
    print(f"生成数据形状: {data.shape}")
    print(f"数据范围: [{data.min():.2f}, {data.max():.2f}]")

    # 一行代码保存全部
    output_dir = gen.save("output/gaussian_grid")
    print(f"保存到: {output_dir}")


if __name__ == "__main__":
    main()