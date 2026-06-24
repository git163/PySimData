"""Example 3: 函数曲线仿真 (sin)"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
from pysimdata.function import FunctionCurve


def main():
    gen = FunctionCurve(func=np.sin, x_range=(0, 2*np.pi), num_points=100, y_shape=50)
    data = gen.generate()
    print(f"生成数据形状: {data.shape}")

    output_dir = gen.save("output/function_curve")
    print(f"保存到: {output_dir}")


if __name__ == "__main__":
    main()