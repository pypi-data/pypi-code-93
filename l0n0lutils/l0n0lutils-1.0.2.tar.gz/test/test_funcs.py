import sys
import os

filepath = os.path.split(__file__)[0]
sys.path.append(".")

from l0n0lutils.funcs import *


s = random_string(100)

print(s)

md5_value = md5(s)

print(md5_value)
