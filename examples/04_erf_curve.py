"""ErfCurve: 误差函数"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pysimdata.function import ErfCurve

gen = ErfCurve(x_range=(-3, 3), num_points=100, y_shape=50)
data = gen.generate()
print(f"ErfCurve: {data.shape}")
gen.save_all("output/erf_curve")