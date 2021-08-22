import shutil
import subprocess
from dataclasses import dataclass
from enum import Enum
from glob import glob
from pathlib import Path
from typing import Dict, Union, List

import orjson
import toml
from loguru import logger
from pbt.poetry import Poetry


class PackageType(str, Enum):
    Poetry = "poetry"


@dataclass
class Package:
    name: str
    type: PackageType
    dir: Path
    version: str
    dependencies: Dict[str, str]
    # list of packages that this package uses
    inter_dependencies: List["Package"]
    # list of packages that use the current package
    invert_inter_dependencies: List["Package"]

    def build(self):
        """Build the package"""
        outfile = f"{self.name}-{self.version}.tar.gz"
        rebuild = True
        if (self.dir / "dist" / outfile).exists():
            if not self.is_modified():
                rebuild = False

        if rebuild:
            logger.info("Build package {}", self.name)
            shutil.rmtree(str(self.dir / "dist"))
            subprocess.check_call(["poetry", "build"], cwd=str(self.dir))

    def is_modified(self) -> bool:
        """Whether the package has been modified since the last version"""
        return True

    def install_into(self, package: "Package", build: bool = False):
        """Install the current package (self) in the virtual environment of another package (`package`)"""
        if build:
            self.build()
        logger.info(
            "Install package {} into package {} environment", self.name, package.name
        )
        pipfile = package.pkg_handler.get_pip_file(package.dir)
        subprocess.check_output([pipfile, "uninstall", "-y", self.name])
        subprocess.check_output([pipfile, "install", self.get_wheel_file()])

    def update_package_version(self, package: "Package"):
        """Update the version of another package in this package"""
        assert package.name in self.dependencies
        self.pkg_handler.update_package(self, package.name, package.version)

    @property
    def pkg_handler(self):
        if self.type == PackageType.Poetry:
            return Poetry
        raise NotImplementedError(self.type)

    def get_wheel_file(self):
        whl_files = glob(str(self.dir / f"dist/{self.name.replace('-', '_')}*.whl"))
        if len(whl_files) == 0:
            return None
        return whl_files[0]

    def to_dict(self):
        return {
            "name": self.name,
            "type": self.type,
            "dir": self.dir,
            "version": self.version,
            "dependencies": self.dependencies,
            "inter_dependencies": [p.name for p in self.inter_dependencies],
            "invert_inter_dependencies": [
                p.name for p in self.invert_inter_dependencies
            ],
        }

    @staticmethod
    def save(packages: Dict[str, "Package"], outfile: Union[str, Path]):
        with open(str(outfile), "wb") as f:
            f.write(
                orjson.dumps(
                    {package.name: package.to_dict() for package in packages.values()}
                )
            )

    @staticmethod
    def load(infile: str) -> Dict[str, "Package"]:
        with open(infile, "r") as f:
            raw_packages = orjson.loads(f.read())
        packages = {name: Package(**o) for name, o in raw_packages}
        for package in packages:
            package.type = PackageType(package.type)
            packages.inter_dependencies = [
                packages[name] for name in package.inter_dependencies
            ]
            packages.invert_inter_dependencies = [
                packages[name] for name in package.invert_inter_dependencies
            ]
        return packages


def search_packages(root_dir: Path):
    logger.info("Search packages...")
    packages = {}

    for poetry_file in glob(str(root_dir / "*/pyproject.toml")):
        poetry_file = Path(poetry_file)
        package_dir = poetry_file.parent

        try:
            with open(poetry_file, "r") as f:
                project_cfg = toml.loads(f.read())
                package_name = project_cfg["tool"]["poetry"]["name"]
                package_version = project_cfg["tool"]["poetry"]["version"]
                package_dependencies = project_cfg["tool"]["poetry"]["dependencies"]
        except:
            logger.error("Error while parsing configuration in {}", package_dir)
            raise

        logger.info("Found package {}", package_name)
        packages[package_name] = Package(
            name=package_name,
            type=PackageType.Poetry,
            version=package_version,
            dependencies=package_dependencies,
            dir=package_dir,
            inter_dependencies=[],
            invert_inter_dependencies=[],
        )

    package_names = set(packages.keys())
    for package in packages.values():
        for pname in package_names.intersection(package.dependencies.keys()):
            package.inter_dependencies.append(packages[pname])
            packages[pname].invert_inter_dependencies.append(package)

    return packages
