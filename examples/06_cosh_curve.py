"""CoshCurve: 双曲余弦"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pysimdata.function import CoshCurve

gen = CoshCurve(x_range=(-2, 2), num_points=100, y_shape=50)
data = gen.generate()
print(f"CoshCurve: {data.shape}")
gen.save("output/cosh_curve")