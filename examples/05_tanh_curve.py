"""TanhCurve: 双曲正切"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pysimdata.function import TanhCurve

gen = TanhCurve(x_range=(-3, 3), num_points=100, y_shape=50)
data = gen.generate()
print(f"TanhCurve: {data.shape}")
gen.save_all("output/tanh_curve")