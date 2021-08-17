import sys
import os
from setuptools import setup, find_packages

__version__ = "2021.1.0"

# 'setup.py publish' shortcut.
if sys.argv[-1] == "publish":
    os.system("python setup.py sdist bdist_wheel")
    os.system("twine upload dist/*")
    sys.exit()

# 'setup.py test' shortcut.
# !pip install --index-url https://test.pypi.org/simple/ sensiml -U
if sys.argv[-1] == "test":
    os.system("python setup.py sdist bdist_wheel")
    os.system("twine upload --repository-url https://test.pypi.org/legacy/ dist/*")
    sys.exit()

setup(
    name="SensiML",
    description="SensiML Analytic Suite Python client",
    version=__version__,
    author="SensiML",
    author_email="support@sensiml.com",
    license="Proprietary",
    classifiers=[
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    packages=find_packages(exclude=["*test*"]),
    package_data={
        "sensiml.datasets": ["*.csv"],
        "sensiml.widgets": ["*.pem"],
        "sensiml.image": ["*.png"],
    },
    include_package_data=True,
    long_description=open("README.md").read(),
    install_requires=[
        "pandas>=1.1.5",
        "cookiejar==0.0.2",
        "requests>=2.14.2",
        "requests-oauthlib>=0.7.0",
        "appdirs==1.4.3",
        "semantic_version>=2.6.0",
        "jupyter>=1.0.0",
        "matplotlib>=2.0.0",
        "nrfutil>=3.3.2,<=5.0.0",
        "qgrid>=1.0.2",
        "prompt-toolkit>=2.0.5",
        "jupyter-console>=6.0.0",
        "notebook==5.7.5",
        "ipython>=7.0.1",
        "ipywidgets>=7.5.1",
        "pywin32==225 ; sys_platform == 'win32'",
        "bqplot",
        "seaborn",
        "wurlitzer",
        "jupyter-contrib-nbextensions",
        "pyserial",
    ],
)
