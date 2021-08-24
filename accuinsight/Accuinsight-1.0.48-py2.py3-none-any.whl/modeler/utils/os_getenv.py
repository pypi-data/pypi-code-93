from __future__ import print_function
import os
import sys
import json
import subprocess
from Accuinsight.modeler.core.LcConst import LcConst

_BASH_RC_PATH = '/home/notebook/.bashrc'


def get_os_env(env_type='LC', env_path=None, env_file=None):
    _ENV_PREFIX = env_type + '_'

    env_value = {}
    if env_path is None:
        env_path = '/home/work'
    if env_file is None:
        env_file = '.env'

    env_file = open(env_path + '/' + env_file, 'r')
    while True:
        line = env_file.readline()
        if not line:
            break
        if line:
            if _ENV_PREFIX in line:
                key, value = line.split('=')
                if key is not None:
                    if _ENV_PREFIX in key:
                        value = value.rstrip()
                        env_value.setdefault(key, value)

    return env_value


def is_in_ipython():
    if 'ipykernel' in sys.modules:
        return True
    return False
    
    
def __list_jupyterlab_workspace(targtet_path):
    file_lists = []
    for (dirpath, dirnames, filenames) in os.walk(targtet_path):
        for fn in filenames:
            if not fn.endswith('.swp'):
                if 'labworkspaces' in fn: continue
                file_lists.append(fn)
            break
    return file_lists


def __get_current_file(target_path, target_file):
    with open(target_path + '/' + target_file, 'r') as tf:
        strlines = tf.readlines()
        aaa = json.loads(strlines[0])
        current_notebook = aaa['data']['layout-restorer:data']['main']['current']
    return current_notebook


def __install_package(package_name):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])


def get_current_notebook():
    if is_in_ipython():
        target_path = LcConst.ENV_JUPYTER_WORKSPACE
        # '/home/notebook/.jupyter/lab/workspaces'
        if os.path.isdir(target_path): # if jupyter lab
            return __get_current_file(target_path=target_path,
                                      target_file=__list_jupyterlab_workspace(targtet_path=target_path)[0]
                                      ).split(':')[1]
        else:
            __install_package('ipyparams')
            import ipyparams
            return ipyparams.notebook_name
