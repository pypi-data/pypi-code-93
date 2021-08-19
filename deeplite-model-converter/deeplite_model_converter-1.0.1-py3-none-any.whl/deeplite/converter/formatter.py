import logging, sys
from enum import Enum

def getLogger():
    nroot = logging.RootLogger(logging.DEBUG)
    consol_level = logging.DEBUG

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(consol_level)
    nroot.addHandler(console_handler)

    return nroot

logger = getLogger()

class ModelFormat(Enum):
    PYTORCH = 'pytorch'
    JIT = 'pytorch-jit'
    ONNX = 'onnx'
    TF = 'tensorflow'
    TFLITE = 'tflite'