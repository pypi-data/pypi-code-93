import subprocess
from functools import wraps
from threading import Thread


def new_thread(func):
    @wraps(func)
    def decorate(*args, **kwargs) -> Thread:
        return run_new_thread(func, *args, **kwargs)
    
    return decorate


def run_new_thread(func, *args, **kwargs) -> Thread:
    t = Thread(target=func, args=args, kwargs=kwargs)
    t.start()
    return t


def send_cmd(cmd: str, ignore_errors=False) -> str:
    try:
        ret = subprocess.run(
            cmd, shell=True, check=True, capture_output=True
        )
        out = ret.stdout.decode(encoding='utf-8').replace('\r\n', '\n')
    except subprocess.CalledProcessError as e:
        out = e.stderr.decode(encoding='utf-8')
        if not ignore_errors:
            raise Exception(out)
    return out
