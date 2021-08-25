#!/usr/bin/env python3

import argparse
import os
import platform
import re
import shutil
import sys
import venv

from distutils import sysconfig
from typing import Generator, List, Optional

import xappt

REQUIRED_PACKAGES = ['PyQt5==5.15.4', 'xappt==0.6.0']

SSH_REGEX = re.compile(r"^(?P<user>[^:]+?)(?::(?P<pass>[^/].*?))?@(?P<host>.*?):(?:(?P<port>\d+)/)?"
                       r"(?P<path>.*?/.*?)$", re.I)
URL_REGEX = re.compile(r"^(?P<protocol>.*?)://(?:(?P<user>.*?)(?::(?P<pass>.*?))?@)?"
                       r"(?P<domain>.*?)(?::(?P<port>\d+))?/(?P<path>.*)$", re.I)

if platform.system() == "Windows":
    VENV_BIN = "Scripts"
    PYTHON_EXT = ".exe"
else:
    VENV_BIN = "bin"
    PYTHON_EXT = ""

PYQT5_INIT_WINDOWS = """
__path__ = __import__('pkgutil').extend_path(__path__, __name__)


def find_qt():
    import os, sys

    qtcore_dll = 'Qt5Core.dll'

    path_var = os.environ['PATH']

    for path in path_var.split(os.pathsep):
        if os.path.isfile(os.path.join(path, qtcore_dll)):
            os.add_dll_directory(path)
            return

    search_paths = [
        os.getcwd(),
        os.path.join(os.path.dirname(__file__), "Qt", "bin"),
    ]

    if sys.executable is not None:
        python_dir = os.path.dirname(sys.executable)
        search_paths.append(python_dir)

    for path in search_paths:
        if os.path.isfile(os.path.join(path, qtcore_dll)):
            os.environ['PATH'] = path + os.pathsep + path_var
            os.add_dll_directory(path)
            return


find_qt()
del find_qt
"""


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()

    parser.add_argument('-s', '--source', help='A git URL to clone, or folder to copy, for the build. If not '
                                               'specified the current code base will be used.')
    parser.add_argument('-b', '--branch', default="master", help='The branch to check out, if source is a git URL')
    parser.add_argument('-o', '--output', help='A folder that will contain the built program.')
    parser.add_argument('-p', '--plugins', action='append', help='Include an external xappt plugins folder or '
                                                                 'git url in the build.')
    parser.add_argument('-t', '--title', help='A custom window title for xappt_qt')
    parser.add_argument('-c', '--console', action='store_true', help='Show the console on Windows')

    return parser


def check_build_requirements():
    if shutil.which("git") is None:
        raise SystemExit("git was not found")
    try:
        import venv
    except ImportError:
        raise SystemExit("venv python module not found")


def resolve_package_string(package_str: str, *, strip_version: bool = False) -> Optional[str]:
    package_str = package_str.strip()

    # ignore blank lines
    if not len(package_str):
        return None

    # ignore comment lines
    if package_str[0] == "#":
        return None

    # strip comments
    package_str = package_str.replace("\t", " ")
    package_str = package_str.split(" #")[0].strip()

    if strip_version:
        for op in ('~=', '==', '!=', '<=', '>=', '<', '>'):  # see PEP 440
            package_str = package_str.split(op)[0].strip()

    if len(package_str):
        return package_str


def packages_from_requirements(req_file_path: str) -> Generator[str, None, None]:
    with open(req_file_path, "r") as fp:
        packages = fp.readlines()
    for package in packages:
        package = resolve_package_string(package)
        if package is not None:
            yield package


class Builder:
    def __init__(self, *, work_path: str):
        self.work_path = work_path
        self.cmd = xappt.CommandRunner(cwd=work_path)
        self.python_bin = None
        self.site_packages = None

    def create_venv(self):
        venv_path = os.path.join(self.work_path, "venv")
        venv.create(venv_path)

        self.python_bin = os.path.join(venv_path, VENV_BIN, 'python' + PYTHON_EXT)
        self.site_packages = sysconfig.get_python_lib(prefix=venv_path)

        install_command = (sys.executable, '-m', 'pip', 'install', 'pip', '-t', self.site_packages)
        if self.cmd.run(install_command, silent=False).result != 0:
            raise SystemExit("Could not install pip into virtual environment")

        self.cmd.env_path_prepend('PATH', os.path.dirname(self.python_bin))
        self.cmd.env_path_prepend('PATH', os.path.join(self.site_packages, 'bin'))
        self.cmd.env_path_prepend('PYTHONPATH', self.site_packages)
        self.cmd.env_var_set('VIRTUAL_ENV', venv_path)
        self.cmd.env_var_remove('PYTHONHOME')

    def install_python_package(self, package_name: str):
        install_command = (self.python_bin, '-m', 'pip', 'install', package_name, '-t', self.site_packages)
        if self.cmd.run(install_command, silent=False).result != 0:
            raise SystemExit(f"Error installing {package_name}")

    def install_python_requirements(self, req_file_path: str, *, exclude: Optional[List[str]] = None):
        if exclude is not None:
            for package in packages_from_requirements(req_file_path):
                package_name = resolve_package_string(package, strip_version=True)
                if package_name in exclude:
                    continue
                self.install_python_package(package)
        else:
            # no exclusions - just a standard requirements.txt install
            install_command = (self.python_bin, '-m', 'pip', 'install', '-r', req_file_path,
                               '-t', self.site_packages)
            if self.cmd.run(install_command, silent=False).result != 0:
                raise SystemExit(f"Error installing {req_file_path}")

    def clone_repository(self, url: str, *, destination: str,  branch: Optional[str] = None):
        if branch is not None:
            git_command = ("git", "clone", "-b", branch, url, destination)
        else:
            git_command = ("git", "clone", url, destination)
        if self.cmd.run(git_command, silent=False).result != 0:
            raise SystemExit(f"Clone of {url} failed")

    def clone_or_copy_repository(self, url: str, *, destination: str, **kwargs) -> str:
        repo_name = os.path.basename(url)
        repo_dest = os.path.join(destination, repo_name)
        if os.path.isdir(url):
            shutil.copytree(url, repo_dest)
            return repo_dest
        else:
            for regex in (SSH_REGEX, URL_REGEX):
                match = regex.match(url)
                if match is not None:
                    self.clone_repository(url=url, destination=repo_dest, **kwargs)
                    return repo_dest
        raise NotImplementedError


def patch_pyqt5(*, site_packages: str):
    if platform.system() != "Windows":
        return
    pyqt_init_path = os.path.join(site_packages, "PyQt5", "utilities/__init__.py")
    assert os.path.isfile(pyqt_init_path)
    os.rename(pyqt_init_path, f"{pyqt_init_path}.bak")
    with open(pyqt_init_path, "w") as fp:
        fp.write(PYQT5_INIT_WINDOWS)


def get_version(version_path: str) -> str:
    with open(version_path, "r") as fp:
        version_contents = fp.read()

    loc = locals()
    exec(version_contents, {}, loc)
    __version__ = loc['__version__']
    assert __version__ is not None

    return __version__


def update_build(version_path: str, new_build: str):
    version = get_version(version_path)
    with open(version_path, "w") as fp:
        fp.write(f'__version__ = "{version}"\n')
        fp.write(f'__build__ = "{new_build}"\n')


def update_app_title(constants_path: str, *, new_title: str):
    with open(constants_path, "r") as fp:
        lines = fp.readlines()

    with open(constants_path, "w") as fp:
        replaced_title = False
        for line in lines:
            if line.startswith('APP_TITLE = '):
                line = f'APP_TITLE = "{new_title}"\n'
                replaced_title = True
            fp.write(line)

    if not replaced_title:
        raise SystemExit(f"APP_TITLE declaration not fount in '{constants_path}'")


def find_qt() -> str:
    import PyQt5

    if platform.system() == "Linux":
        qt5_bin = "lib"
        qt5core_lib = "libQt5Core.so.5"
    elif platform.system() == "Windows":
        qt5_bin = "bin"
        qt5core_lib = "Qt5Core.dll"
    else:
        raise NotImplementedError

    bin_path = os.path.join(os.path.dirname(PyQt5.__file__), "Qt", qt5_bin)
    if os.path.isfile(os.path.join(bin_path, qt5core_lib)):
        return bin_path

    raise FileNotFoundError("Could not find PyQt5's QtCore library")


def inject_plugin_import(plugin_path: str, *, target_file: str, line_num: int):
    with open(target_file, "r") as fp:
        lines = fp.readlines()

    prefix = "".join(lines[:line_num])
    suffix = "".join(lines[line_num:])

    plugin_name = os.path.splitext(os.path.basename(plugin_path))[0]

    import_lines = ""
    for plugin in (plugin_name, f"{plugin_name}.plugins"):
        import_lines += f"\ntry:\n    import {plugin}\nexcept ImportError:\n    pass\n\n"

    with open(target_file, "w") as fp:
        fp.write(prefix)
        fp.write(import_lines)
        fp.write(suffix)


def main(args) -> int:
    check_build_requirements()

    parser = build_parser()
    options = parser.parse_args(args=args)

    output_path = os.path.abspath(options.output)
    if os.path.isdir(output_path):
        raise SystemExit(f"Error, output path exists: {output_path}")

    with xappt.temp_path() as tmp:
        builder = Builder(work_path=tmp)
        builder.create_venv()

        if options.source is not None:
            repo_path = builder.clone_or_copy_repository(options.source, destination=tmp, branch=options.branch)
            req_path = os.path.join(repo_path, "requirements.txt")
            builder.install_python_requirements(req_path)
            version_path = os.path.join(repo_path, 'xappt_qt', '__version__.py')
            commit_id = xappt.git_tools.commit_id(repo_path, short=True)
            update_build(version_path, commit_id)
        else:
            repo_path = os.path.join(tmp, "xappt_qt")
            root_path = os.path.dirname(os.path.dirname(__file__))
            shutil.copytree(root_path, repo_path)
            for package in REQUIRED_PACKAGES:
                builder.install_python_package(package)

        entry_point = os.path.join(repo_path, "xappt_qt", "main.py")
        assert os.path.isfile(entry_point)

        plugins_destination = os.path.join(tmp, "plugins")
        for plugin in options.plugins or []:  # in case options.plugins is None
            plugin_path = builder.clone_or_copy_repository(plugin, destination=plugins_destination)
            req_file = os.path.join(plugin_path, "requirements.txt")
            if os.path.isfile(req_file):
                builder.install_python_requirements(req_file, exclude=["xappt", "xappt-qt"])
            inject_plugin_import(plugin_path, target_file=entry_point, line_num=8)
            builder.cmd.env_path_prepend("PYTHONPATH", plugin_path)

        if options.title is not None:
            constants_path = os.path.join(repo_path, "xappt_qt", "constants.py")
            update_app_title(constants_path, new_title=options.title)

        builder.cmd.env_path_prepend("PATH", find_qt())

        patch_pyqt5(site_packages=builder.site_packages)

        nuitka_package = "nuitka==0.6.9.2"
        builder.install_python_package(nuitka_package)

        nuitka_command = ["python", "-m", "nuitka", "--standalone", "--recurse-all",
                          f"--windows-icon={os.path.join(repo_path, 'xappt_qt', 'resources', 'icons', 'appicon.ico')}",
                          "--plugin-enable=qt-plugins", f"--output-dir={output_path}"]

        if not options.console:
            nuitka_command.append("--windows-disable-console")

        nuitka_command.append(entry_point)

        builder.cmd.run(nuitka_command, silent=False)

    return 0


if __name__ == '__main__':
    if sys.version_info[:2] < (3, 7):
        raise SystemExit("Python 3.7 or higher is required.")
    sys.exit(main(sys.argv[1:]))
