"""Example 3: 函数曲线仿真"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
from pysimdata.function import FunctionCurve


def main():
    output_dir = "output/function_curve"
    os.makedirs(output_dir, exist_ok=True)

    func_names = ["sin", "cos", "tan"]

    try:
        import matplotlib.pyplot as plt

        fig, axes = plt.subplots(1, 3, figsize=(12, 4))

        for i, func_name in enumerate(func_names):
            config = {"type": "FunctionCurve", "format": "npy", "params": {"func": func_name, "x_range": [0, 2*np.pi], "num_points": 100, "y_shape": 50}}
            gen = FunctionCurve.from_config(config)
            data = gen.generate()

            if i == 0:
                np.save(os.path.join(output_dir, "data.npy"), data)
                gen.save_config(os.path.join(output_dir, "config.json"))
                print(f"保存到: {output_dir}")

            y = data[0, :]
            x = np.linspace(0, 2*np.pi, len(y))
            axes[i].plot(x, y)
            axes[i].set_title(f"func={func_name}")
            axes[i].grid(True)

        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, "preview.png"), dpi=150)
        plt.close()
    except ImportError:
        for i, func_name in enumerate(func_names):
            config = {"type": "FunctionCurve", "format": "npy", "params": {"func": func_name, "num_points": 100}}
            gen = FunctionCurve.from_config(config)
            data = gen.generate()
            if i == 0:
                np.save(os.path.join(output_dir, "data.npy"), data)
                print(f"生成数据形状: {data.shape}")
                print(f"保存到: {output_dir}")


if __name__ == "__main__":
    main()