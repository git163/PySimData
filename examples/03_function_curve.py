"""Example 3: 函数曲线仿真"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
from pysimdata.function import FunctionCurve


def main():
    output_dir = "output/function_curve"
    os.makedirs(output_dir, exist_ok=True)

    # 不同函数
    funcs = ["sin", "cos", "tan"]
    configs = [
        {"type": "FunctionCurve", "format": "npy", "params": {"func": f, "x_range": [0, 2*np.pi], "num_points": 100, "y_shape": 50}}
        for f in funcs
    ]

    try:
        import matplotlib.pyplot as plt

        fig, axes = plt.subplots(1, 3, figsize=(12, 4))

        for i, config in enumerate(configs):
            gen = FunctionCurve.from_config(config)
            data = gen.generate()

            # 保存第一个
            if i == 0:
                np.save(os.path.join(output_dir, "data.npy"), data)
                gen.save_config(os.path.join(output_dir, "config.json"))
                print(f"保存到: {output_dir}")

            # 绘图
            axes[i].imshow(data, cmap="viridis", aspect="auto")
            axes[i].set_title(f"func={config['params']['func']}")
            axes[i].axis("off")

        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, "preview.png"), dpi=150)
        plt.show()
    except ImportError:
        # 不绘图，只生成数据
        for i, config in enumerate(configs):
            gen = FunctionCurve.from_config(config)
            data = gen.generate()
            if i == 0:
                np.save(os.path.join(output_dir, "data.npy"), data)
                gen.save_config(os.path.join(output_dir, "config.json"))
                print(f"生成数据形状: {data.shape}")
                print(f"保存到: {output_dir}")


if __name__ == "__main__":
    main()