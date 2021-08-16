# helpers.py
from pathlib import Path

from importlib import resources as importlib_resources
import shutil
import subprocess

from akerbp.mlops.core import logger, config 
from akerbp.mlops import __version__


logging=logger.get_logger(name='mlops_deployment')

env = config.envs.env
service_name = config.envs.service_name


def get_repo_origin():
    origin = subprocess.check_output(
        ['git', 'remote', 'get-url', '--push', 'origin'],
        encoding='UTF-8'
    ).rstrip()
    return origin


def replace_string_file(s_old, s_new, file):
    """
    Replaces all occurrences of s_old with s_new in a file
    """
    with file.open() as f:
        s = f.read()
        if s_old not in s:
            logging.warning(f"Didn't find '{s_old}' in {file}")

    with file.open('w') as f:
        s = s.replace(s_old, s_new)
        f.write(s)


def set_mlops_import(req_file):
    package_version = __version__
    replace_string_file('MLOPS_VERSION', package_version, req_file)
    logging.info(f"Set akerbp.mlops=={package_version} in requirements.txt")


def to_folder(path, folder_path):
    """
    Copy folders, files or package data to a given folder.
    Note that if target exists it will be overwritten.
    Input:
      - path: supported formats
            - file/folder path (Path): e,g, Path("my/folder")
            - module file (tuple/list): e.g. ("my.module", "my_file"). Module
            path has to be a string, but file name can be a Path object. 
    """
    if isinstance(path, (tuple,list) ):
        module_path, file = path
        file = str(file)
        if importlib_resources.is_resource(module_path, file):
            with importlib_resources.path(module_path, file) as file_path:
                shutil.copy(file_path, folder_path)
        else:
            raise ValueError(f"Didn't find {path[1]} in {path[0]}")
    elif path.is_dir():
        shutil.copytree(path, folder_path/path, dirs_exist_ok=True)
    elif path.is_file():
        shutil.copy(path, folder_path)
    else:
        raise ValueError(f"{path} should be a file, folder or package resource")


def copy_to_deployment_folder(list, deployment_folder):
    """
    Copy a list of files/folders to a deployment folder
    
    Input:
        - list: (dictionary), key is the nick name of the file/folder (used for
        logging) and the value is the path (see `to_folder` for supported
        formats)
        - deployment_folder: (Path) 
    """
    for k,v in list.items():
        logging.debug(f"{k} => deployment folder")
        to_folder(v, deployment_folder)


def install_requirements(req_file):
    logging.info(f"Install python requirement file {req_file}")
    c = ["pip", "install", "-r", req_file]
    subprocess.check_call(c)


def set_up_requirements(c):
    """
    Set up a "requirements.txt" file at the top of the deployment folder
    (assumed to be the current directory), update config and install
    dependencies (unless in dev)
    """
    logging.info("Create requirement file")

    set_mlops_import(c.req_file)
    shutil.move(c.req_file, 'requirements.txt')
    c.req_file = 'requirements.txt'
    if env != "dev":
        install_requirements('requirements.txt')


def deployment_folder_path(model):
    return Path(f'mlops_{model}')


def rm_deployment_folder(model):
    logging.debug(f"Delete deployment folder")
    deployment_folder = deployment_folder_path(model)
    if deployment_folder.exists():
        shutil.rmtree(deployment_folder)