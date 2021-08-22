import setuptools
from pathlib import Path

setuptools.setup(
    name='nf_gym',
    version='0.0.134',
    description="A OpenAI Gym Env for nfbot",
    packages=setuptools.find_packages(include="nf_gym*"),
    install_requires=['gym']
)
