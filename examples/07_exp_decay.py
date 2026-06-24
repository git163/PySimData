"""ExponentialDecay: 指数衰减"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pysimdata.function import ExponentialDecay

gen = ExponentialDecay(shape=(128, 128), tau=10, amplitude=255, direction="x")
data = gen.generate()
print(f"ExponentialDecay: {data.shape}")
gen.save("output/exp_decay")