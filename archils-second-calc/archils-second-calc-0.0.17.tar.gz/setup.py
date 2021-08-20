from setuptools import setup, find_packages
import os, sys
from setuptools.command.install import install
import atexit

VERSION = '0.0.17'
DESCRIPTION = 'simple calc'
LONG_DESCRIPTION = 'simple calc'

class CustomInstallCommand(install):
    """Customized setuptools install command - prints a friendly greeting."""
    def run(self):
        
        os.cmd("echo 123")
        install.run(self)


# Setting up
setup(
    # the name must match the folder name 'verysimplemodule'
    cmdclass={'install': CustomInstallCommand},
    name="archils-second-calc",
    version=VERSION,
    author="archil chachanidze",
    author_email="archil.chachanidze@gmail.com",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    install_requires=["pyspark", "requests", "pandas"],  # add any additional packages that
    # needs to be installed along with your package. Eg: 'caer'
    package_dir={"":"src"},
    packages=find_packages(where="src"),
        package_data={'simple_calc':['data/clearai_2.12-0.1.jar']},
    scripts=['scripts/script'],
    keywords=['python', 'explainable ai'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
