import setuptools
from pathlib import Path

setuptools.setup(
    name = "pbtoyrobot",
    version = "1.0.10",
    author = "Paolo Benini",
    description = "A simple project for a toy robot",
    long_description = Path("README.md").read_text(),
    long_description_content_type = "text/markdown",
    packages = setuptools.find_packages(include = ["pbtoyrobot", "tests"]),
    package_data = {"pbtoyrobot": ["*.yaml"]},
    include_package_data = True,
    install_requires = ["pyyaml"],
    entry_points = {
        "console_scripts": [
            "pbtoyrobot = pbtoyrobot.__main__:main"
        ]
    }
)