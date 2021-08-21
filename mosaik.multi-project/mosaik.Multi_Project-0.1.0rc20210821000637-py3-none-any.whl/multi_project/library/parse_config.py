import platform
from pathlib import Path
from typing import Dict

import sys


def parse_project_config(
    *,
    projects_path: Path,
    simulator: Dict,
):
    alias = simulator['alias']
    repository = simulator['repository']
    branch = simulator['branch']
    project_path = simulator['project_path']
    container_name = simulator['container_name']
    venv_python_name = simulator['venv_python_name']

    repo_path = projects_path / alias

    project_path = repo_path / project_path if project_path else repo_path

    venv_path = project_path / 'venv'

    venv_python_path = ''
    if (
        venv_python_name is not None and
        isinstance(venv_python_name, str)
    ):
        if len(venv_python_name) not in (len('python3'), len('python3.9')):
            raise NotImplementedError(
                f'Cannot handle venv environment name {venv_python_name}.'
                'Please use venv environment names like "python3" or '
                '"python3.9".'
            )

        if platform.system() == 'Linux':
            venv_python_path = venv_path / 'bin' / venv_python_name
        if platform.system() == 'Windows':
            venv_python_path = venv_path / 'Scripts' / venv_python_name
    else:
        venv_python_path = None

    # Clamp the configured python version for tox to the current interpreter
    # TODO Detect whether or not the requested python version is installed
    tox_environment_name = simulator['tox_environment_name']
    if (
        tox_environment_name is not None and
        isinstance(tox_environment_name, str) and
        tox_environment_name.startswith('py')
    ):
        if len(tox_environment_name) != 4:
            raise NotImplementedError(
                f'Cannot handle tox environment name {tox_environment_name}.'
                'Please use pytest-style environment names.'
            )
        tox_environment_name = \
            tox_environment_name[:-2] + \
            str(sys.version_info.major) + \
            str(sys.version_info.minor)
    else:
        tox_environment_name = None

    tox_python_path = None
    if tox_environment_name:
        tox_python_path = \
            project_path / '.tox' / tox_environment_name / 'bin' / 'python'

    tox_requirements_txt_file_path = \
        simulator['tox_requirements_txt_file_path']
    if tox_requirements_txt_file_path:
        tox_requirements_txt_file_path = \
            project_path / tox_requirements_txt_file_path

    venv_requirements_txt_file_path = \
        simulator['venv_requirements_txt_file_path']
    if venv_requirements_txt_file_path:
        venv_requirements_txt_file_path = \
            project_path / venv_requirements_txt_file_path

    return alias, branch, project_path, repo_path, repository, \
        venv_python_name, venv_python_path,\
        tox_environment_name, tox_python_path, tox_requirements_txt_file_path, \
        container_name, venv_requirements_txt_file_path
