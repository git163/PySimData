"""FunctionCurve: 函数曲线"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pysimdata.function import FunctionCurve

gen = FunctionCurve(func=__import__('numpy').sin, x_range=(0, 6.28), num_points=100, y_shape=50)
data = gen.generate()
print(f"FunctionCurve: {data.shape}")
gen.save_all("output/function_curve")