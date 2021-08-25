import ctypes
import os
import os.path
import platform
import sys

# check architecture
arch = platform.machine()
print("System architecture: ", arch)

# load libraries
if arch == "x86_64" or arch == "amd64":
    basepath = os.path.dirname(__file__) + "/bin/x64"
elif arch == "aarch64":
    basepath = os.path.dirname(__file__) + "/bin/arm64"
else:
    sys.exit("Failed to load libraries: Unknown architecture")

#ctypes.CDLL(os.path.abspath(os.path.join(basepath, "libsystemd.so")), mode=ctypes.RTLD_GLOBAL)
ctypes.CDLL("libsystemd.so.0", mode=ctypes.RTLD_GLOBAL)
__libzmq_name = os.path.abspath(os.path.join(basepath, "libzmq.so.5"))
if os.path.isfile(__libzmq_name):
    ctypes.CDLL(__libzmq_name, mode=ctypes.RTLD_GLOBAL)
else:
    sys.exit("Failed to load libraries: '{}' does not exists".format(__libzmq_name))

libcomm_datalayer = None
__libname = os.path.abspath(os.path.join(basepath, "libcomm_datalayer.so"))
if os.path.isfile(__libname):
    libcomm_datalayer = ctypes.CDLL(__libname)
else:
    sys.exit("Failed to load libraries: '{}' does not exists".format(__libname))

# typedef enum DLR_RESULT
C_DLR_RESULT = ctypes.c_int32

userData_c_void_p = ctypes.c_void_p
address_c_char_p = ctypes.c_char_p
