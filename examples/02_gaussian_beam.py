"""Example 2: 高斯束斑仿真"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
from pysimdata.function import GaussianBeam


def main():
    output_dir = "output/gaussian_beam"
    os.makedirs(output_dir, exist_ok=True)

    # 方式 1: 直接创建
    print("=" * 50)
    print("高斯束斑仿真")
    gen = GaussianBeam(shape=(256, 256), sigma=20, amplitude=255, center=(128, 128))
    data = gen.generate()
    print(f"生成数据形状: {data.shape}")
    print(f"峰值: {data.max():.2f}")

    # 保存
    np.save(os.path.join(output_dir, "data.npy"), data)
    gen.save_config(os.path.join(output_dir, "config.json"))
    print(f"保存到: {output_dir}")

    # 方式 2: 从配置字典
    print("\n" + "=" * 50)
    config = {
        "type": "GaussianBeam",
        "format": "png",
        "params": {
            "shape": [128, 128],
            "sigma": 10,
            "amplitude": 255,
            "center": [64, 64],
        },
    }
    gen2 = GaussianBeam.from_config(config)
    data2 = gen2.generate()
    print(f"生成数据形状: {data2.shape}")

    # 绘图 (可选)
    print("\n" + "=" * 50)
    print("绘图")
    try:
        import matplotlib.pyplot as plt

        fig, axes = plt.subplots(1, 2, figsize=(8, 4))
        axes[0].imshow(data, cmap="hot")
        axes[0].set_title("sigma=20")
        axes[1].imshow(data2, cmap="hot")
        axes[1].set_title("sigma=10")
        for ax in axes:
            ax.axis("off")
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, "preview.png"), dpi=150)
        plt.close()
    except ImportError:
        print("matplotlib 未安装，跳过绘图")


if __name__ == "__main__":
    main()