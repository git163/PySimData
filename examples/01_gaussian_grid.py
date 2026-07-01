"""GaussianGrid: 高斯点阵"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pysimdata.function import GaussianGrid

gen = GaussianGrid(shape=(128, 128), mean=0, std=1, num_points=9, seed=42)
data = gen.generate()
print(f"GaussianGrid: {data.shape}")
gen.save_all("output/gaussian_grid")