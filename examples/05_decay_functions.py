"""Example 5: 衰减函数仿真"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
from pysimdata.function import ExponentialDecay, BilateralGaussian


def main():
    output_dir = "output/decay_functions"
    os.makedirs(output_dir, exist_ok=True)

    generators = [
        (ExponentialDecay(shape=(128, 128)), "exp_decay", "x方向"),
        (ExponentialDecay(shape=(128, 128), direction="y"), "exp_decay_y", "y方向"),
        (BilateralGaussian(shape=(128, 128)), "bilateral_gaussian", "双边高斯"),
    ]

    try:
        import matplotlib.pyplot as plt

        fig, axes = plt.subplots(1, 3, figsize=(12, 4))

        for i, (gen, name, title) in enumerate(generators):
            data = gen.generate()

            # 保存第一个
            if i == 0:
                np.save(os.path.join(output_dir, "data.npy"), data)
                gen.save_config(os.path.join(output_dir, "config.json"))
                print(f"保存到: {output_dir}")

            axes[i].imshow(data, cmap="gray", aspect="auto")
            axes[i].set_title(title)
            axes[i].axis("off")

        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, "preview.png"), dpi=150)
        plt.show()
    except ImportError:
        for i, (gen, name, title) in enumerate(generators):
            data = gen.generate()
            if i == 0:
                np.save(os.path.join(output_dir, "data.npy"), data)
                gen.save_config(os.path.join(output_dir, "config.json"))
                print(f"生成数据形状: {data.shape}")
                print(f"保存到: {output_dir}")


if __name__ == "__main__":
    main()