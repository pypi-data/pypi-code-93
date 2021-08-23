import time
import sys
import subprocess
import contextlib
import psutil
import os
import functools
import random
import string


def get_random_string(length):
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str

@contextlib.contextmanager
def setup_api_server(port=8080):
    dbfile_path = "/tmp/" + get_random_string(20) + "-test.db"
    try:
        bin_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "api-server")
        proc = subprocess.Popen([bin_path, "-dbType", "sqlite3", "-dbFilePath", dbfile_path, "-port", str(port)])

        while True:
            p = psutil.Process(proc.pid)
            listens =  [x for x in p.connections() if x.status == psutil.CONN_LISTEN]
            if len(listens) > 0:
                break
            time.sleep(1)

        yield
    except Exception as e:
        raise e
    finally:
        proc.terminate()
        subprocess.run(["rm", dbfile_path])