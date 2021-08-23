import io
import os
import re
from setuptools import find_packages
from setuptools import setup
from os import path
import os

with open('requirements.txt') as f:
    install_reqs = f.read().splitlines()

for req in install_reqs:
    os.system("python -m pip install {}".format(req))

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="power_cogs",
    url="https://github.com/kragniz/cookiecutter-pypackage-minimal",
    license='MIT',

    author="Shyam Sudhakaran",
    author_email="shyamsnair@protonmail.com",

    description="A set of useful research templates for deep learning projects",

    long_description=long_description,
    long_description_content_type="text/markdown",

    packages=find_packages(exclude=('tests',)),

    install_requires=[
        'tensorboard==2.4.0',
        'torch',
        'hydra-core==1.1.0.rc1',
        'pydantic',
        'numpy',
        'attrs',
        'loguru',
        'torchsummaryX',
        'matplotlib',
        'einops',
        'tqdm',
        'ipython==7.23.1',
        'ipywidgets',
        'ipython-genutils==0.2.0',
        'wcwidth',
        'ptyprocess==0.6.0',
        'pytz',
        'ansible-please',
        'gym',
        'docker==3.7.0',
        'wandb==0.9.7',
        'omegaconf==2.1.0.rc1'
    ],

    include_package_data=True,

    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.8',
    ],
    version='0.1.1',
    zip_safe=False,
)

