"""Example 4: 特殊函数仿真 (erf)"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pysimdata.function import ErfCurve


def main():
    gen = ErfCurve(x_range=(-3, 3), num_points=100, y_shape=50)
    data = gen.generate()
    print(f"生成数据形状: {data.shape}")

    output_dir = gen.save("output/special_functions")
    print(f"保存到: {output_dir}")


if __name__ == "__main__":
    main()