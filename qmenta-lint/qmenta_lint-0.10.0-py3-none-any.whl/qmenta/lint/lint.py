# -*- coding: utf-8 -*-
# This is a standalone file compatible with py2 and py3

import multiprocessing
import os
import shlex
import subprocess
import sys
from functools import partial

import yaml
from tabulate import tabulate

py_versions = [3.6, 3.8, 3.9]
flake8_flags = "--max-line-length 120"


def find_repo_dir(path):
    path = os.path.abspath(path)
    if path == "/":
        raise RuntimeError("This tool should run inside a repository directory!")
    elif os.path.isdir(os.path.join(path, ".git")):
        return path
    else:
        return find_repo_dir(os.path.join(path, os.path.pardir))


def iter_components(path):
    """
    Recursively search for components with a build.yaml specification.

    Parameters
    ----------
    path : str
        Path where search starts.

    Returns
    -------
    list of str
        List of paths to the found components
    """
    build_file = os.path.join(path, "build.yaml")
    if os.path.isfile(build_file):
        return [path]
    elif os.path.isdir(path):
        components = []
        for subdir in os.listdir(path):
            components += iter_components(os.path.join(path, subdir))
        return components
    else:
        return []


def lint(compatible_components, component_id):
    component = compatible_components[component_id]
    if not component.get("lint", False):
        return

    output = []

    output.append("\nChecking {} ...".format(component["id"]))
    pythonpath = ":".join([compatible_components[c_id]["path"] + "/python" for c_id in component["dependencies"]])
    cmds_str = "{python} -m flake8 {path}/python {flags}".format(
        python=sys.executable, path=component["path"], flags=flake8_flags
    )
    if pythonpath:
        output.append("PYTHONPATH={}".format(pythonpath))
    new_env = os.environ.copy().update({"PYTHONPATH": pythonpath})
    process = subprocess.Popen(
        shlex.split(cmds_str), stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=new_env, universal_newlines=True
    )
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        if stdout:
            output.append(stdout.rstrip())
        if stderr:
            output.append(stderr.rstrip())
        output.append("❌ Linting failed!")
    else:
        output.append("✔️  Looking good!")

    return output


def parse_build_file(path):
    with open(path, "r") as stream:
        contents = yaml.safe_load(stream)
    contents["path"] = os.path.dirname(path)
    contents["id"] = os.path.basename(contents["path"])
    contents["version"] = str(contents["version"])
    if "requirements" not in contents:
        contents["requirements"] = []
    if "requirements_file" in contents:
        full_path = os.path.join(contents["path"], contents["requirements_file"])
        if not os.path.isfile(full_path):
            raise RuntimeError("Cannot find requirements file: {!r}".format(full_path))
        with open(full_path, "r") as fd:
            contents["requirements"] += fd.read().splitlines()
    return contents


def get_python_package_components(sources):
    filtered_components = []
    for component_src in sources:
        new_component = parse_build_file(os.path.join(component_src, "build.yaml"))
        if new_component["type"] == "python_package":
            filtered_components.append(new_component)
    return filtered_components


def main():
    current_dir = os.getcwd()
    repo_dir = find_repo_dir(current_dir)
    current_version = "{}.{}".format(sys.version_info.major, sys.version_info.minor)
    print("Python: {} ({})".format(current_version, sys.executable))
    print("Repository: {}".format(repo_dir))
    print("flake8 Flags: {}\n".format(flake8_flags))

    components_sources = iter_components(repo_dir)
    components = get_python_package_components(components_sources)

    # Show state
    headers = ["Package"] + py_versions
    data = []
    compatible_components = {}
    for component in components:
        row = ["{} {}".format(component["id"], "" if component.get("lint", False) else "(no lint)")]
        for py_version in py_versions:
            if py_version in component["python_compatibility"]:
                row.append("yes")
                if str(py_version) == str(current_version):
                    compatible_components[component["id"]] = component
            else:
                row.append("no")
        data.append(row)

    print(tabulate(data, headers=headers))

    to_lint = [c for c in compatible_components if compatible_components[c].get("lint", False)]
    cores = multiprocessing.cpu_count()
    if not to_lint:
        print("\nNothing to do here 🤷‍")
    else:
        print(
            "\nChecking {} packages using {} cores (compatible with current python version {})...".format(
                len(to_lint), cores, current_version
            )
        )

    p = multiprocessing.Pool(cores)
    lint_id = partial(lint, compatible_components)
    returns = p.map(lint_id, to_lint)
    for ret in returns:
        print("\n".join(ret))


if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter
