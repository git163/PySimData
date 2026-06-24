"""Example 4: 特殊函数仿真 (erf, tanh, cosh)"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
from pysimdata.function import ErfCurve, TanhCurve, CoshCurve


def main():
    output_dir = "output/special_functions"
    os.makedirs(output_dir, exist_ok=True)

    # (生成器, 函数名, 标题)
    gens = [
        (ErfCurve(x_range=(-3, 3), ), "erf", "Error Function"),
        (TanhCurve(x_range=(-3, 3), ), "tanh", "Hyperbolic Tangent"),
        (CoshCurve(x_range=(-2, 2), ), "cosh", "Hyperbolic Cosine"),
    ]

    try:
        import matplotlib.pyplot as plt
        fig, axes = plt.subplots(1, 3, figsize=(12, 4))

        for i, (gen, name, title) in enumerate(gens):
            data = gen.generate()
            if i == 0:
                np.save(os.path.join(output_dir, "data.npy"), data)
                gen.save_config(os.path.join(output_dir, "config.json"))
                print(f"保存到: {output_dir}")

            y = data[0, :]
            x = np.linspace(-3 if name != "cosh" else -2, 3 if name != "cosh" else 2, len(y))
            axes[i].plot(x, y, label=name)
            axes[i].set_title(title)
            axes[i].grid(True)
            axes[i].legend()

        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, "preview.png"), dpi=150)
        plt.close()
    except ImportError:
        for i, (gen, name, title) in enumerate(gens):
            data = gen.generate()
            if i == 0:
                np.save(os.path.join(output_dir, "data.npy"), data)
                print(f"生成数据形状: {data.shape}")


if __name__ == "__main__":
    main()