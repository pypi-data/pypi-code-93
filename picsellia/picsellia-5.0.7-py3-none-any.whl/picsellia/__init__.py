__version__ = "5.0.7"

import sys
import os 
from setuptools import find_packages
import picsellia
for p in find_packages(where=picsellia.__path__[0]):
    sys.path.append(os.path.join(picsellia.__path__[0],p.replace('.','/')))

sys.path.append(picsellia.__path__[0])
