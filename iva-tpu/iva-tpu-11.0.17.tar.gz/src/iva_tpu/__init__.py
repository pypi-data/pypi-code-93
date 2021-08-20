import importlib.util
import sys
spec = importlib.util.spec_from_file_location("libtpu", "/usr/lib/libtpu.so")
libtpu = importlib.util.module_from_spec(spec)
sys.modules["iva_tpu"] = libtpu
