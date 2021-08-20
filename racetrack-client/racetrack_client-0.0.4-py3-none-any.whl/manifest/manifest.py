from dataclasses import dataclass
from typing import Optional, List


@dataclass
class Manifest:
    """Fatman Manifest file - build recipe to get deployable image from source code workspace"""

    # name of the Fatman Workload
    name: str

    git: 'GitManifest'

    # version of the Manifest file
    version: str = '1'

    # Language wrapper used to embed model
    lang: str = 'python3'

    # Python-specific configuration
    python: Optional['PythonManifest'] = None

    # Go/Golang-specific configuration
    golang: Optional['GoManifest'] = None

    # Docker-specific configuration
    docker: Optional['DockerManifest'] = None

    # type of deployed image: docker image, packer, AMI
    image_type: str = 'docker'

    # system-wide packages that should be installed with apt
    system_dependencies: Optional[List[str]] = None


@dataclass
class PythonManifest:
    requirements_path: Optional[str] = None
    # path to a Python file with a entrypoint class
    entrypoint_path: str = ''
    # base name of Python entrypoint class
    entrypoint_class: str = ''


@dataclass
class GoManifest:
    # relative path to Go modules requirements
    gomod: str = 'go.mod'


@dataclass
class GitManifest:
    # URL of git remote: HTTPS, SSH or directory path to a remote repository
    remote: str
    branch: Optional[str] = None
    # subdirectory relative to git repo root
    directory: str = '.'


@dataclass
class DockerManifest:
    dockerfile_path: Optional[str] = None
