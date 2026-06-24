"""Example 1: 高斯点阵仿真"""
import os
from datetime import datetime

import numpy as np

# 添加父目录到路径
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pysimdata.function import GaussianGrid


def main():
    # 输出目录
    output_dir = "output/gaussian_grid"
    os.makedirs(output_dir, exist_ok=True)

    # 方式 1: 直接创建并生成
    print("=" * 50)
    print("方式 1: 直接创建")
    gen = GaussianGrid(shape=(128, 128), mean=0, std=1, num_points=5, seed=42)
    data = gen.generate()
    print(f"生成数据形状: {data.shape}")
    print(f"数据范围: [{data.min():.2f}, {data.max():.2f}]")

    # 保存数据和配置
    data_path = os.path.join(output_dir, "data.npy")
    np.save(data_path, data)
    config_path = os.path.join(output_dir, "config.json")
    gen.save_config(config_path)
    print(f"保存数据到: {data_path}")
    print(f"保存配置到: {config_path}")

    # 方式 2: 从字典加载配置
    print("\n" + "=" * 50)
    print("方式 2: 从字典加载配置")
    config_dict = {
        "type": "GaussianGrid",
        "format": "npy",
        "params": {
            "shape": [64, 64],
            "mean": 0,
            "std": 1,
            "num_points": 3,
        },
    }
    gen2 = GaussianGrid.from_config(config_dict)
    data2 = gen2.generate()
    print(f"生成数据形状: {data2.shape}")

    # 方式 3: 从 JSON 文件加载配置
    print("\n" + "=" * 50)
    print("方式 3: 从 JSON 文件加载配置")
    gen3 = GaussianGrid.from_config(config_path)
    data3 = gen3.generate()
    print(f"生成数据形状: {data3.shape}")

    # 绘图 (可选)
    print("\n" + "=" * 50)
    print("绘图")
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib 未安装，跳过绘图")
        return

    fig, axes = plt.subplots(1, 3, figsize=(12, 4))
    axes[0].imshow(data, cmap="gray")
    axes[0].set_title("方式1: 直接创建")
    axes[1].imshow(data2, cmap="gray")
    axes[1].set_title("方式2: 字典配置")
    axes[2].imshow(data3, cmap="gray")
    axes[2].set_title("方式3: 文件配置")
    for ax in axes:
        ax.axis("off")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "preview.png"), dpi=150)
    print(f"保存预览图到: {os.path.join(output_dir, 'preview.png')}")
    plt.close()


if __name__ == "__main__":
    main()