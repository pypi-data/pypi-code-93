import sys

import os

from setuptools import setup, find_packages


__version__ = "2021.2.0"


# 'setup.py publish' shortcut.

if sys.argv[-1] == "publish":
    os.system("python setup_dev.py sdist bdist_wheel")
    os.system("twine upload dist/*")
    sys.exit()


# 'setup.py test' shortcut.

# !pip install --index-url https://test.pypi.org/simple/ sensiml -U

if sys.argv[-1] == "test":
    os.system("python setup_dev.py sdist bdist_wheel")
    os.system("twine upload --repository-url https://test.pypi.org/legacy/ dist/*")
    sys.exit()


setup(
    name="sensiml-dev",
    description="SensiML Analytic Suite Python Dev Client",
    version=__version__,
    author="SensiML",
    author_email="support@sensiml.com",
    license="Proprietary",
    classifiers=[
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    packages=find_packages(exclude=["*test*", "*widgets*"]),
    package_data={"sensiml.datasets": ["*.csv"],},
    include_package_data=True,
    long_description=open("README.md").read(),
    install_requires=[
        "cookiejar==0.0.2",
        "requests>=2.14.2",
        "requests-oauthlib>=0.7.0",
        "appdirs==1.4.3",
        "semantic_version>=2.6.0",
        "numpy",
        "pandas",
        "matplotlib",
        "prompt-toolkit",
        "seaborn",
        "wurlitzer",
        "pyserial",
    ],
)
