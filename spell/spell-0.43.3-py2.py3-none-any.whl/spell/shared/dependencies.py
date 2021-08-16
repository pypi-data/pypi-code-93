import subprocess
import sys
from pip_chill import chill
import requirements
import yaml

from spell.api.models import RunRequest
from spell.shared.projects import get_project_by_name


FRAMEWORK_PACKAGES = {
    "tensorflow",
    "keras",
    "pytorch",
    "torchvision",
    "pytorch-lightning",
    "requests",
    "pandas",
    "numpy",
    "matplotlib",
    "scikit-learn",
    "xgboost",
    "spell",
}


def get_base_prefix_compat():
    """Get base/real prefix, or sys.prefix if there is none."""
    return getattr(sys, "base_prefix", None) or getattr(sys, "real_prefix", None) or sys.prefix


def in_virtualenv():
    return get_base_prefix_compat() != sys.prefix


class NoEnvFound(RuntimeError):
    message = "Could not find an active conda environment or virtualenv"


class NoVirtualEnvFound(NoEnvFound):
    message = "Could not find an active virtualenv"


class InvalidDependencyConfig(Exception):
    def __init__(self, message):
        self.message = message


class PipDependencies:
    def __init__(self, deps, overridden_framework_packages=None):
        self.deps = deps
        self.overridden_framework_packages = overridden_framework_packages or []

    @classmethod
    def from_env(cls):
        if not in_virtualenv():
            raise NoVirtualEnvFound
        deps = chill(no_chill=True)[0]
        mock_requirements_file = "\n".join([f"{dep.name}=={dep.version}" for dep in deps])
        reqs = requirements.parse(mock_requirements_file)
        filtered_reqs = [r for r in reqs if r.name not in FRAMEWORK_PACKAGES]
        return cls(deps=filtered_reqs)

    @classmethod
    def from_requirements_file(cls, requirements_file_path):
        try:
            with open(requirements_file_path, "r") as requirement_file:
                try:
                    reqs = requirements.parse(requirement_file)
                    filtered_reqs = [r for r in reqs if r.name not in FRAMEWORK_PACKAGES]
                    return cls(deps=filtered_reqs)
                except Exception:
                    requirement_file.seek(0)
                    unparsable_requirement = cls.identify_unparsable_requirement(
                        requirement_file.readlines()
                    )
                    raise InvalidDependencyConfig(
                        f"Could not parse requirement {unparsable_requirement} in requirements file "
                        f"at {requirements_file_path}"
                    )
        except Exception:
            raise InvalidDependencyConfig(
                f"Could not open pip requirements file at {requirements_file_path}"
            )

    @classmethod
    def from_strings(cls, requirements_strings):
        try:
            reqs = list(requirements.parse("\n".join(requirements_strings)))
        except Exception:
            unparsable_requirement = cls.identify_unparsable_requirement(requirements_strings)
            raise InvalidDependencyConfig(f"Could not parse requirement {unparsable_requirement}")

        overridden_packages = [r for r in reqs if r.name in FRAMEWORK_PACKAGES]
        # Unlike other methods, this allows a user to override framework images
        return cls(deps=list(reqs), overridden_framework_packages=overridden_packages)

    @staticmethod
    def identify_unparsable_requirement(requirement_strings):
        for requirement in requirement_strings:
            try:
                requirements.parse(requirement)
            except Exception:
                return requirement

    def update(self, more_deps):
        self.deps = self._merge_dependency_list(self.deps, more_deps.deps)
        self.overridden_framework_packages = self._merge_dependency_list(
            self.overridden_framework_packages,
            more_deps.overridden_framework_packages,
        )

    @staticmethod
    def _merge_dependency_list(base_deps, other_deps):
        base_deps = {dep.name: dep for dep in base_deps}
        other_deps = {dep.name: dep for dep in other_deps}
        base_deps.update(other_deps)
        return list(base_deps.values())

    def as_package_list(self):
        return self.to_pip_names(self.deps)

    @staticmethod
    def to_pip_names(package_list):
        return sorted([dep.line for dep in package_list])

    @staticmethod
    def to_pip_str(package_list):
        return "\n".join(PipDependencies.to_pip_names(package_list))

    def __str__(self):
        return self.to_pip_str(self.deps)


class CondaDependencies:
    def __init__(self, environment):
        self.environment = environment

    @classmethod
    def from_env(cls):
        env_out = subprocess.run(
            ["conda", "env", "export", "--from-history"], stdout=subprocess.PIPE
        )
        if env_out.returncode != 0:
            raise InvalidDependencyConfig(
                "Could not export current conda environment. "
                f"Running 'conda env export --from-history' returned exit code {env_out.returncode} "
            )
        try:
            environment = yaml.safe_load(env_out.stdout)
        except Exception as e:
            raise InvalidDependencyConfig(f"Could not parse current conda environment. Got {e}")

        environment.pop("name")
        environment.pop("prefix", None)
        return cls(environment=environment)

    @classmethod
    def from_file(cls, conda_file_path):
        try:
            with open(conda_file_path) as conda_file:
                try:
                    environment = yaml.safe_load(conda_file)
                    return cls(environment=environment)
                except Exception:
                    raise InvalidDependencyConfig(
                        f"Conda Environment file at {conda_file_path} could not be parsed"
                    )
        except Exception:
            raise InvalidDependencyConfig(
                f"Could not open Conda Environment file at {conda_file_path}",
            )

    def dump(self):
        return yaml.dump(self.environment)

    def __str__(self):
        return self.dump()


def split_pip_conda(python_deps):
    if not python_deps:
        return [], None
    if isinstance(python_deps, PipDependencies):
        return python_deps.as_package_list(), None
    else:
        return [], python_deps.dump()


def get_pip_conda_dependencies(kwargs):
    """
    Parses code package specification kwargs and returns lists of pip and conda dependencies.
    These parameters (and hence, this code) is shared between the run and model server create
    APIs.
    """
    # grab conda env file contents
    python_deps = merge_dependencies(
        None,
        kwargs.pop("conda_file", None),
        kwargs.pop("requirements_file", None),
        kwargs.pop("pip_packages", []),
    )
    pip, conda = split_pip_conda(python_deps)
    return pip, conda


def merge_dependencies(python_env_deps, conda_file, requirements_file, pip_packages):
    python_deps = python_env_deps
    if conda_file is not None:
        if python_env_deps:
            # TODO(justin): Conda has a merge-environments script which can handle this logic
            raise InvalidDependencyConfig(
                "Merging dependencies from a conda environment and a conda file is not currently supported"
            )
        return CondaDependencies.from_file(conda_file)

    if isinstance(python_deps, CondaDependencies):
        if pip_packages or requirements_file:
            # TODO(justin): Conda envs are yamls, so we should be able to handle this case
            raise InvalidDependencyConfig(
                "pip packages and requirements files cannot currently be specified when using a conda environment. "
                "You can include the pip installs in the conda environment file instead."
            )
        return python_deps

    if requirements_file:
        req_file_deps = PipDependencies.from_requirements_file(requirements_file)
        if not python_deps:
            python_deps = req_file_deps
        else:
            python_deps.update(PipDependencies.from_requirements_file(requirements_file))
    if pip_packages:
        pip_deps = PipDependencies.from_strings(pip_packages)
        if not python_deps:
            python_deps = pip_deps
        else:
            python_deps.update(PipDependencies.from_strings(pip_packages))
    return python_deps


def get_run_request(client, kwargs):
    """Converts an python API request's kwargs to a RunRequest"""
    pip, conda = get_pip_conda_dependencies(kwargs)
    # set workflow id
    if "workflow_id" not in kwargs and client.active_workflow:
        kwargs["workflow_id"] = client.active_workflow.id
    if "project" in kwargs:
        project = kwargs.pop("project")
        existing_projects = client.api.list_projects()

        # NOTE(aleksey): throws if a project with this name does not already exist
        project = get_project_by_name(existing_projects, project)
        kwargs["project_id"] = project.id

    return RunRequest(
        run_type="user",
        pip_packages=pip,
        conda_file=conda,
        **kwargs,
    )
