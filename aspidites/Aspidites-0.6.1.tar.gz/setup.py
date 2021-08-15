#!/usr/bin/python3
import os
from setuptools import setup, find_packages
from setuptools.dist import Distribution
from setuptools.command.install import install
from Aspidites import __version__, compiler, parser
from Aspidites.__main__ import get_cy_kwargs

cy_kwargs = get_cy_kwargs()
cy_kwargs.update({'embed': True})
code = open('Aspidites/woma/library.wom', 'r').read()
compiler.compile_module(
    parser.parse_module(code),
    'Aspidites/woma/library.pyx',
    bytecode=True,
    **cy_kwargs
)


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


# Tested with wheel v0.29.0
class BinaryDistribution(Distribution):
    """Distribution which always forces a binary package with platform name"""
    def has_ext_modules(foo):
        return True


class InstallWrapper(install):
    """Provides a install wrapper for native woma
    extensions. These don't really belong in the
    Python package."""

    def run(self):
        # Run this first so the install stops in case
        # these fail otherwise the Python package is
        # successfully installed
        print("running preinstall hooks")
        self.preinstall()
        install.run(self)  # pip install
        print("running postinstall hooks")
        self.postinstall()

    def preinstall(self):
        """preinstall hook"""
        c = "Aspidites build/lib/Aspidites/woma/library.wom -c -o build/lib/Aspidites/woma/library.pyx --embed=True"
        os.popen(c)
        print(c)
        pass

    def postinstall(self):
        """postinstall hook"""
        pass


setup(
    name="Aspidites",
    version=__version__,
    author="Ross J. Duff",
    author_email="rjdbcm@mail.umkc.edu",
    description="Aspidites is the reference implementation of the Woma Language",
    license="GPL",
    keywords="language",
    url="https://github.com/rjdbcm/Aspidites",
    install_requires=[
        'pyrsistent',
        'numpy',
        'cython>0.28,<3',
        'pyparsing',
        'mypy',
        'pytest',
        'future'
        ],
    packages=find_packages(),
    distclass=BinaryDistribution,
    entry_points={'console_scripts': ['aspidites = Aspidites.__main__:main']},
    package_data={'': ["*.wom", "*.pyx", "*.pyi"]},  # add any native *.wom files
    long_description=read('README.md'),
    cmdclass={'install': InstallWrapper},
    long_description_content_type='text/markdown',
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
    ],
)
