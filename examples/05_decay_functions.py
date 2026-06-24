"""Example 5: 衰减函数仿真 (指数衰减)"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pysimdata.function import ExponentialDecay


def main():
    gen = ExponentialDecay(shape=(128, 128), tau=10, amplitude=255, direction="x")
    data = gen.generate()
    print(f"生成数据形状: {data.shape}")

    output_dir = gen.save("output/decay_functions")
    print(f"保存到: {output_dir}")


if __name__ == "__main__":
    main()