from .gaiaengine import *
import os
os.environ["PYSDL2_DLL_PATH"] = os.path.join(os.path.dirname(__file__), ".dylibs")
os.environ["GAIA_SHADERS_PATH"] = os.path.dirname(__file__)
