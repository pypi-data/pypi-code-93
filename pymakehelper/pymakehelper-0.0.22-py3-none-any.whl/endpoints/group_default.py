"""
The default group of operations that pymakehelper has
"""

import os  # for walk, getcwd, symlink, listdir, unlink, mkdir
import os.path  # for join, expanduser, realpath, abspath, islink, isdir, isfile
import subprocess
import sys

from pytconf import register_endpoint, register_function_group, get_free_args

from pymakehelper.configs import ConfigSymlinkInstall

import pymakehelper
import pymakehelper.version
from pymakehelper.utils import touch_mkdir_many, no_err_run

GROUP_NAME_DEFAULT = "default"
GROUP_DESCRIPTION_DEFAULT = "all pymakehelper commands"


def register_group_default():
    """
    register the name and description of this group
    """
    register_function_group(
        function_group_name=GROUP_NAME_DEFAULT,
        function_group_description=GROUP_DESCRIPTION_DEFAULT,
    )


@register_endpoint(
    group=GROUP_NAME_DEFAULT,
)
def version() -> None:
    """
    Print version
    """
    print(pymakehelper.version.VERSION_STR)


def debug(msg):
    """debug function for the symlink install operation"""
    if ConfigSymlinkInstall.debug:
        print(msg)


def do_install(source, target):
    """install a single item"""
    if ConfigSymlinkInstall.force:
        if os.path.islink(target):
            os.unlink(target)
    if ConfigSymlinkInstall.doit:
        debug('symlinking [{0}], [{1}]'.format(source, target))
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


@register_endpoint(
    configs=[
        ConfigSymlinkInstall,
    ],
    group=GROUP_NAME_DEFAULT,
)
def symlink_install() -> None:
    """
    Install symlinks to things in a folder
    """
    cwd = os.getcwd()
    if os.path.isdir(ConfigSymlinkInstall.target_folder):
        for file in os.listdir(ConfigSymlinkInstall.target_folder):
            full = os.path.join(ConfigSymlinkInstall.target_folder, file)
            if os.path.islink(full):
                link_target = os.path.realpath(full)
                if link_target.startswith(cwd):
                    if ConfigSymlinkInstall.doit:
                        debug('unlinking [{0}]'.format(full))
                        os.unlink(full)
    else:
        os.mkdir(ConfigSymlinkInstall.target_folder)
    for root, directories, files in file_gen(ConfigSymlinkInstall.source_folder, ConfigSymlinkInstall.recurse):
        for file in files:
            source = os.path.abspath(os.path.join(root, file))
            target = os.path.join(ConfigSymlinkInstall.target_folder, file)
            do_install(source, target)
        for directory in directories:
            source = os.path.abspath(os.path.join(root, directory))
            target = os.path.join(ConfigSymlinkInstall.target_folder, directory)
            do_install(source, target)


@register_endpoint(
    group=GROUP_NAME_DEFAULT,
    allow_free_args=True,
)
def remove_folders() -> None:
    """
    Remove one folder from each file name
    """
    result = []
    for filename in get_free_args():
        # r = os.path.splitext(os.sep.join(filename.split(os.sep)[1:]))[0]
        r = os.sep.join(filename.split(os.sep)[1:])
        result.append(r)
    print(' '.join(result), end='')


@register_endpoint(
    group=GROUP_NAME_DEFAULT,
    allow_free_args=True,
)
def touch_mkdir() -> None:
    """
    Touch a folder, possibly creating folders for it
    """
    touch_mkdir_many(get_free_args())


@register_endpoint(
    group=GROUP_NAME_DEFAULT,
    allow_free_args=True,
)
def no_err() -> None:
    """
    Return with no error even if underlying process returns error
    """
    no_err_run(get_free_args())


@register_endpoint(
    group=GROUP_NAME_DEFAULT,
    allow_free_args=True,
)
def only_print_on_error() -> None:
    """
    Collect stdout and stderr and print them only if the command
    produced an error
    """
    pr = subprocess.Popen(get_free_args(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (out_out, out_err) = pr.communicate()
    status = pr.returncode
    if status:
        print(out_out.decode(), end='')
        print(out_err.decode(), end='')
        sys.exit(status)
