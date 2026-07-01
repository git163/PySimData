"""load: 从 save_all 目录整体恢复（配置 + 数据）"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pysimdata import GaussianGrid, load

# 先生成并保存（默认 csv、无时间戳）
gen = GaussianGrid(shape=(128, 128), num_points=9, seed=42)
gen.generate()
out = gen.save_all("output/load_demo")
print(f"saved to: {out}")

# 从目录整体恢复：数据直接来自 data.csv，不重算
restored = load(out)
print(f"restored data shape: {restored.data.shape}")
print(f"restored params: {restored.params}")
