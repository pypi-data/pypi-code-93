"""
Facilitates the isolation of NEURON simulators by running them in subprocesses.
"""

import os
import sys
import codecs
import inspect
import tempfile
import functools
import subprocess as _sp
from tblib import pickling_support
import dill

# Install `traceback` pickling support so that the worker's exception tracebacks
# can be sent back over stderr
pickling_support.install()
# Locate the worker script
_worker_script = os.path.join(os.path.dirname(__file__), "_worker.py")
# Marks boundaries between a serialized object and stderr/stdout junk.
_boundary = "|!|!|!|!|!|!|!|!|!|"
# Bytes version of the boundary
_boundary_bytes = bytes(_boundary, "utf-8")

def _get_obj_module_path(obj):
    # Find the path that should be added to PATH on the worker so that `obj`'s
    # module' can be imported on the worker.
    p = inspect.getfile(obj)
    d = os.path.dirname(p)
    if p.endswith("__init__.py"):
        return os.path.dirname(d)
    return d

def subprocess(f, *args, _worker_path=None, **kwargs):
    """
    Run a function on a subprocess.
    """
    if _worker_path is None:
        _worker_path = []
    result = _invoke(f, args, kwargs, _worker_path)
    return result

def _invoke(f, args, kwargs, paths):
    objstr = _obj2str((f, args, kwargs))
    # Virtual files to write subprocess' stdout & stderr to.
    o, e = tempfile.SpooledTemporaryFile(), tempfile.SpooledTemporaryFile()
    try:
        try:
            process = _sp.Popen([sys.executable, _worker_script, objstr, repr(paths)], stdout=o, stderr=e)
            process.communicate()
        except Exception as e:
            print("Uncaught Popen exception.")
            raise
        if process.returncode == 1:
            # Exit code nonzero: ERR
            # Unpack the Exception that the worker has written to stderr and
            # raise it.
            e.seek(0)
            ex = _unpack_worker_result(e.read())
            raise ex
        elif process.returncode == 0:
            # Exit code 0: OK
            # Unpack the results that the worker wrote to stdout
            o.seek(0)
            return _unpack_worker_result(o.read())
        else:
            # Exit code unknown: child crashed
            o.seek(0)
            e.seek(0)
            print(" --- stdout ---")
            print(o.read().decode("utf-8"))
            print(" --- stderr ---")
            print(e.read().decode("utf-8"))
            raise RuntimeError("Child process crashed.")
    finally:
        o.close()
        e.close()

def _obj2str(obj):
    dillbytes = dill.dumps(obj)
    return codecs.encode(dillbytes, "base64").decode("utf-8")

def _b64bytes2obj(b64bytes):
    dillbytes = codecs.decode(b64bytes, "base64")
    return dill.loads(dillbytes)

def _unpack_worker_data(data):
    b64bytes = bytes(data, "utf-8")
    return _b64bytes2obj(b64bytes)

def _write_worker_result(result):
    sys.stdout.write(_boundary + _obj2str(result) + _boundary)

def _write_worker_error(err):
    sys.stderr.write(_boundary + _obj2str(err) + _boundary)

def _unpack_worker_result(result):
    c = result.count(_boundary_bytes)
    if c != 2:
        raise RuntimeError(f"Subprocess communication error. Received {c} data boundary signals, expected 2.")
    b64bytes = result.split(_boundary_bytes)[1]
    bytestream = codecs.decode(b64bytes, "base64")
    return dill.loads(bytestream)

def isolate(f=None, worker_path=None):
    """
    Decorator to run the decorated function in an isolated subprocess.
    """
    @functools.wraps(f)
    def subprocessor(*args, **kwargs):
        return subprocess(f, *args, _worker_path=worker_path, **kwargs)
    if f is not None:
        return subprocessor
    def decorator(f_inner):
        nonlocal f
        f = f_inner
        return subprocessor
    return decorator
