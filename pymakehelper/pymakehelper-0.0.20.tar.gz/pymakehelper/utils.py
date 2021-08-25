import logging
import os
import subprocess

from pymakehelper.static import APP_NAME


def ensure_dir(f):
    folder = os.path.dirname(f)
    if folder != '' and not os.path.isdir(folder):
        os.makedirs(folder)


def touch(f):
    if os.path.isfile(f):
        os.utime(f, None)
    else:
        with open(f, 'w'):
            pass


def touch_mkdir(f):
    ensure_dir(f)
    touch(f)


def touch_mkdir_many(filenames):
    for filename in filenames:
        touch_mkdir(filename)


def no_err_run(args):
    subprocess.call(args)


def get_logger():
    return logging.getLogger(APP_NAME)


def debug(msg):
    """debug function for the symlink install operation"""
    logger = get_logger()
    logger.debug(msg)


def do_install(source, target, force: bool, doit: bool):
    """install a single item"""
    if force:
        if os.path.islink(target):
            os.unlink(target)
    if doit:
        debug("symlinking [{source}], [{target}]")
        os.symlink(source, target)


def file_gen(root_folder: str, recurse: bool):
    """generate all files in a folder"""
    if recurse:
        for root, directories, files in os.walk(root_folder):
            yield root, directories, files
    else:
        directories = []
        files = []
        for file in os.listdir(root_folder):
            full = os.path.join(root_folder, file)
            if os.path.isdir(full):
                directories.append(file)
            if os.path.isfile(full):
                files.append(file)
        yield root_folder, directories, files
