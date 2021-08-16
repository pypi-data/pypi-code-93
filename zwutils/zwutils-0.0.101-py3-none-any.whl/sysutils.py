import os
import re
import sys
import psutil
import subprocess
from .fileutils import writefile

def ismac():
    return True if sys.platform == 'darwin' else False

def iswin():
    return True if sys.platform == 'win32' else False

def write_pidfile(dir='.'):
    pid = os.getpid()
    pth = os.path.join(dir, '%s.pid'%pid)
    writefile(pth, pid)
    return pth

def pids_by_name(nm=None):
    rtn = []
    for proc in psutil.process_iter(['pid', 'name']):
        pinfo = proc.info
        pname = pinfo['name']
        if nm:
            _regex = re.compile(nm)
            iscontained = bool(_regex.search(pname))
            if iscontained:
                rtn.append(pinfo)
                continue
        else:
            rtn.append(pinfo)
    rtn = sorted(rtn, key=lambda o: o['name'])
    return rtn

def run_shell(cmd, *args):
    cmds = [cmd]
    cmds.extend(list(args))
    r = subprocess.run(cmds, stdout=subprocess.PIPE).stdout.decode('utf-8')
    return r

def get_sys_usage():
    return {
        'mem': psutil.virtual_memory().percent,
        'cpu': psutil.cpu_percent(None),
    }