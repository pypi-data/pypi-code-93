#!/usr/bin/env python3

import glob
import os
import sys
import subprocess
from setuptools import setup
import distutils.cmd
import distutils.log
from warnings import warn

if sys.version_info.major != 3:
    raise RuntimeError("SCRIdb requires Python 3")
if sys.version_info.minor < 6:
    warn("Some methods may not function properly on Python versions < 3.6")


class RShinyCommand(distutils.cmd.Command):
    """
    A custom command to install RShiny package.
    """

    description = "install RShiny package"
    user_options = [
        ("R-path=", None, "path to Rscript command"),
        ("R-lib=", None, "path to R library trees"),
    ]

    def initialize_options(self):
        """Set default values for options."""
        self.R_path = ""
        self.R_lib = ""

    def finalize_options(self):
        """Post-process options."""
        if self.R_path:
            assert os.path.exists(self.R_path), "command {} does not exist.".format(
                self.R_path
            )
        if self.R_lib:
            assert os.path.exists(
                self.R_lib
            ), "location of R library trees {} does not exist.".format(self.R_lib)

    def run(self):
        """Run command."""
        pkg = glob.glob("R/*.tar.gz")
        if self.R_path:
            R = self.R_path
        else:
            R = "R"
        if self.R_lib:
            R_lib = ", lib='{}'".format(self.R_lib)
        else:
            R_lib = ""

        dependencies = [
            "DBI",
            "RMySQL",
            "DT",
            "htmlwidgets",
            "shiny",
            "shinythemes",
            "shinydashboard",
            "base64enc"
        ]
        dpnd = "c({})".format(",".join(["'{}'".format(i) for i in dependencies]))
        subprocess.call(
            [
                R,
                "--no-save",
                "-e",
                "install.packages({}, repos='https://cloud.r-project.org' {})".format(
                    dpnd, R_lib
                ),
            ]
        )

        command = [
            R,
            "--no-save",
            "-e",
            "install.packages('{}', repos = NULL, dependencies = TRUE {})".format(
                pkg[0], R_lib
            ),
        ]
        self.announce(
            "Executing command: %s" % str(" ".join(command)), level=distutils.log.INFO
        )
        proc = subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )
        outs, errs = proc.communicate()
        if outs:
            print("outs", outs.decode("utf-8"))
        if errs:
            print("errs", errs.decode("utf-8"))
        proc.terminate()


# get version
with open("src/SCRIdb/version.py") as f:
    exec(f.read())

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    cmdclass={"RShiny": RShinyCommand,},
    name="SCRIdb",
    version=__version__,
    package_dir={"": "src"},
    packages=["SCRIdb"],
    scripts=[
        "src/scripts/scridb",
        "src/scripts/update_IGOdates",
        "src/scripts/projectsHTML_index",
        "src/scripts/create-job",
    ],
    url="https://github.com/dpeerlab/SCRI_db.git",
    author=__author__,
    author_email=__email__,
    description="A platform to handle sequencing data submission and initiation of "
    "projects, and to interact with the lab's database - insert meta data, and "
    "interactively pull reports and views.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=[
        "bs4",
        "mysql-connector-python",
        "pandas",
        "ipywidgets",
        "lxml",
        "IPython",
        "regex",
        "python-dateutil",
        "PyYAML",
        "tabulate",
        "boto3",
        "numpy",
        "botocore",
        "nltk",
        "packaging"
    ],
    setup_requires=[
        "bs4",
        "mysql-connector-python",
        "pandas",
        "ipywidgets",
        "lxml",
        "IPython",
        "regex",
        "python-dateutil",
        "PyYAML",
        "tabulate",
        "boto3",
        "numpy",
        "botocore",
        "nltk",
        "packaging"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
