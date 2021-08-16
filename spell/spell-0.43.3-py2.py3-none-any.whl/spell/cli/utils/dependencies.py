import os
import click

from spell.shared.dependencies import (
    FRAMEWORK_PACKAGES,
    PipDependencies,
    CondaDependencies,
    in_virtualenv,
    NoEnvFound
)
from spell.cli.exceptions import ExitException


def dependencies_from_env():
    if os.environ.get("CONDA_DEFAULT_ENV"):
        return CondaDependencies.from_env()
    elif in_virtualenv():
        return PipDependencies.from_env()
    raise NoEnvFound


def confirm_dependencies(python_deps, python_env_deps, requirements_file, pip_packages, force):
    if force or not (python_env_deps or (requirements_file and pip_packages)):
        return

    is_pip_env = isinstance(python_deps, PipDependencies)
    environment_type = "Pip" if is_pip_env else "Conda"
    deps_str = str(python_deps)
    if not deps_str:
        click.confirm(
            f"No dependencies found in {environment_type} environment. Is this correct?",
            default=True,
            abort=True,
        )
    else:
        click.secho(f"Using Python {environment_type} environment:", bold=True)
        click.echo(str(python_deps))
        if is_pip_env:
            click.secho("With additional Python packages from framework:", bold=True)
            if python_deps.overridden_framework_packages:
                overridden_names = {dep.name for dep in python_deps.overridden_framework_packages}
                click.echo(
                    "\n".join(
                        sorted([dep for dep in FRAMEWORK_PACKAGES if dep not in overridden_names])
                    )
                )
                click.secho(
                    "The following framework package versions will be overridden:", bold=True
                )
                click.echo(python_deps.to_pip_str(python_deps.overridden_framework_packages))
            else:
                click.echo("\n".join(sorted(list(FRAMEWORK_PACKAGES))))
        click.confirm("Is this environment correct?", default=True, abort=True)


def validate_pip(pip):
    if pip.find("==") != pip.find("="):
        raise ExitException(
            f"Invalid pip dependency {pip}: = is not a valid operator. Did you mean == ?"
        )


def format_pip_apt_versions(pip, apt):
    if pip:
        for x in pip:
            validate_pip(x)
        pip = [convert_name_version_pair(x, "==") for x in pip]
    if apt:
        apt = [convert_name_version_pair(x, "=") for x in apt]
    return (pip, apt)


def convert_name_version_pair(package, separator):
    split = package.split(separator)
    return {"name": split[0], "version": split[1] if len(split) > 1 else None}
