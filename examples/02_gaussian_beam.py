"""Example 2: 高斯束斑仿真"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pysimdata.function import GaussianBeam


def main():
    gen = GaussianBeam(shape=(256, 256), sigma=20, amplitude=255, center=(128, 128))
    data = gen.generate()
    print(f"生成数据形状: {data.shape}")
    print(f"峰值: {data.max():.2f}")

    output_dir = gen.save("output/gaussian_beam")
    print(f"保存到: {output_dir}")


if __name__ == "__main__":
    main()