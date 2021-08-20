from setuptools import setup, find_packages
import os, sys
from distutils.core import setup
from distutils.command.install import install as _install

VERSION = '0.0.11'
DESCRIPTION = 'simple calc'
LONG_DESCRIPTION = 'simple calc'

def _post_install(dir):
    from subprocess import call
    call([sys.executable, 'scripts/script.py'],
         cwd=os.path.join(dir, 'archils-second-calc'))
class install(_install):
    def run(self):
        _install.run(self)
        self.execute(_post_install, (self.install_lib,),
                     msg="Running post install task")
# Setting up
setup(
    # the name must match the folder name 'verysimplemodule'
    cmdclass={'install': install},
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
