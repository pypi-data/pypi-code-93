from os import path as os_path
from distutils.core import setup
from setuptools import find_packages

path = os_path.abspath(os_path.dirname(__file__))

def read_file(filename):
    with open(os_path.join(path, filename), encoding='utf-8') as f:
        long_description = f.read()
    return long_description

def read_requirements(filename):
    return [line.strip() for line in read_file(filename).splitlines()
            if not line.startswith('#')]

# This call to setup() does all the work
setup(
    name="autosparksql",
    version="1.0.0",
    python_requires = '>=3.5.1',
    description="create sql from config files",
    long_description=read_file("README.md"),
    long_description_content_type="text/markdown",
    author="Henry Liu",
    author_email="2224546920@qq.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3"
    ],
    install_requires=['pymssql'],
    packages=find_packages(exclude=("tests",)),
    include_package_data=True,
)
