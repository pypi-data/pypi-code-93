import subprocess

import click
from typing import List

from loguru import logger

from pbt.config import PBTConfig
from pbt.package import search_packages
from pbt.pypi import PyPI


@click.group()
def cli():
    pass


@click.command()
@click.option(
    "-p",
    "--package",
    multiple=True,
    help="Specify the active package that we are working on. If empty, use all packages",
)
@click.option("--cwd", default="", help="Override current working directory")
def make(package: List[str], cwd: str = ""):
    print(package)
    pbt_cfg = PBTConfig.from_dir(cwd)
    active_packages = package
    packages = search_packages(pbt_cfg)
    if len(active_packages) == 0:
        active_packages = packages.keys()
    active_packages = set(active_packages)
    if len(active_packages.difference(packages.keys())) > 0:
        raise Exception(
            f"Passing unknown packages: {active_packages.difference(packages.keys())}. Available options: {list(packages.keys())}"
        )

    for package in packages.values():
        if package.is_modified():
            logger.info("Package {} has been modified", package.name)
            parent_packages = [
                pp
                for pp in package.invert_inter_dependencies
                if pp.name in active_packages
            ]
            if len(parent_packages) > 0:
                package.build()
                for pp in parent_packages:
                    package.install_into(pp, build=False)
                    pp.update_package_version(package)


@click.command()
@click.option("--cwd", default="", help="Override current working directory")
def publish(cwd: str = ""):
    pbt_cfg = PBTConfig.from_dir(cwd)
    packages = search_packages(pbt_cfg)
    for package in packages.values():
        if PyPI.does_package_exist(package.name, package.version):
            logger.info("Skip publishing package {} as it exists", package.name)
            continue
        logger.info("Publish package {}", package.name)
        package.build()
        for pp in package.invert_inter_dependencies:
            pp.update_package_version(package)
        subprocess.check_call(["poetry", "publish"], cwd=str(package.dir))


cli.add_command(make)
cli.add_command(publish)


if __name__ == "__main__":
    cli()
