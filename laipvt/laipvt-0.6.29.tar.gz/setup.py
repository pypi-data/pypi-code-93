from os import path as os_path
from setuptools import setup

import laipvt

this_directory = os_path.abspath(os_path.dirname(__file__))

def read_file(filename):
    with open(os_path.join(this_directory, filename), encoding='utf-8') as f:
        long_description = f.read()
    return long_description

def read_requirements(filename):
    return [line.strip() for line in read_file(filename).splitlines()
            if not line.startswith('#')]

setup(
    name='laipvt',
    entry_points={
        'console_scripts': ['laipvt=laipvt.cli.main:main'],
    },
    python_requires='>=3.6.0',
    version=laipvt.__version__,
    description="laiye private deploy basement",
    long_description="laiye private deploy basement",
    long_description_content_type="text/markdown",
    author="ye",
    author_email='liye@laiye.com',
    url='https://laiye.com',
    packages= [
        "laipvt",
        "laipvt.controller",
        "laipvt.controller.kubernetes",
        "laipvt.controller.middleware",
        "laipvt.controller.service",
        "laipvt.handler",
        "laipvt.helper",
        "laipvt.interface",
        "laipvt.model",
        "laipvt.sysutil",
        "laipvt.cli",
        "upgrade"
    ],
    install_requires=read_requirements('requirements.txt'),
    include_package_data=True,
    license="MIT",
    keywords=['laipvt'],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
)