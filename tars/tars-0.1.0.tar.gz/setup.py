from setuptools import find_packages, setup

setup(
    name='tars',
    packages=find_packages(),
    version='0.1.0',
    description='A cryptocurrency trading bot for research',
    author='Fred Montet',
    license='MIT',
    package_dir={"tars": "src.tars"},
)
