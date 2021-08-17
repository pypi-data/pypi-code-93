import nrnsub, sys, traceback
from tblib import pickling_support

pickling_support.install()

path_instructions = eval(sys.argv[2])
sys.path.extend(path_instructions)
f, args, kwargs = nrnsub._unpack_worker_data(sys.argv[1])
try:
    r = f(*args, **kwargs)
except Exception as e:
    nrnsub._write_worker_error(e)
    exit(1)
else:
    nrnsub._write_worker_result(r)
