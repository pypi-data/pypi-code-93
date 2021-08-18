from setuptools import find_packages, setup
from setuptools.command.test import test as TestCommand

import versioneer

PACKAGE_NAME = "pyrcmip"
DESCRIPTION = "Tools for accessing RCMIP data"
KEYWORDS = ["data", "simple climate model", "climate", "scm"]

AUTHORS = [
    ("Zeb Nicholls", "zebedee.nicholls@climate-energy-college.org"),
    ("Jared Lewis", "jared.lewis@climate-energy-college.org"),
]
EMAIL = "zebedee.nicholls@climate-energy-college.org"
URL = "https://gitlab.com/rcmip/pyrcmip"
PROJECT_URLS = {
    "Bug Reports": "https://github.com/rcmip/pyrcmip/issues",
    # "Documentation": "https://rcmip.readthedocs.io/en/latest",
    "Source": "https://gitlab.com/rcmip/pyrcmip",
}
LICENSE = "3-Clause BSD License"
CLASSIFIERS = [
    "Development Status :: 4 - Beta",
    "License :: OSI Approved :: BSD License",
    "Intended Audience :: Developers",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3.5",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
]

REQUIREMENTS = [
    "boto3",
    "click",
    "docutils<0.16",
    "matplotlib",
    "openpyxl",
    "pyjwt>=2",
    "seaborn",
    "scipy",
    "scmdata>=0.7.3",
    "seaborn>=0.11.0",
    "semver",
    "tqdm",
]
REQUIREMENTS_NOTEBOOKS = [
    "ipywidgets",
    "netcdf4",
    "notebook",
    "openscm-twolayermodel",
]
REQUIREMENTS_TESTS = [
    "codecov",
    "nbval",
    "pytest-cov",
    "pytest-mock",
    "pytest>=5.0.0",
    "moto==1.3.14",
]
REQUIREMENTS_DOCS = [
    "sphinx>=3",
    "sphinxcontrib-bibtex>=2",
    "sphinx_click",
    "sphinx_rtd_theme",
]
REQUIREMENTS_DEPLOY = ["twine>=1.11.0", "setuptools>=38.6.0", "wheel>=0.31.0"]
REQUIREMENTS_ZENODO = ["openscm-zenodo"]

REQUIREMENTS_DEV = [
    *["awscli", "flake8", "isort>=5", "black==19.10b0", "pydocstyle", "nbdime"],
    *REQUIREMENTS_NOTEBOOKS,
    *REQUIREMENTS_TESTS,
    *REQUIREMENTS_DOCS,
    *REQUIREMENTS_DEPLOY,
    *REQUIREMENTS_ZENODO,
]

REQUIREMENTS_EXTRAS = {
    "docs": REQUIREMENTS_DOCS,
    "notebooks": REQUIREMENTS_NOTEBOOKS,
    "tests": REQUIREMENTS_TESTS,
    "deploy": REQUIREMENTS_DEPLOY,
    "dev": REQUIREMENTS_DEV,
    "zenodo": REQUIREMENTS_ZENODO,
}

SOURCE_DIR = "src"

PACKAGES = find_packages(SOURCE_DIR)  # no exclude as only searching in `src`
PACKAGE_DIR = {"": SOURCE_DIR}
PACKAGE_DATA = {"": ["data/*.xlsx"]}

ENTRY_POINTS = {"console_scripts": ["rcmip = pyrcmip.cli:run_cli"]}

README = "README.rst"

with open(README, "r") as readme_file:
    README_TEXT = readme_file.read()


class RCMIP(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest

        pytest.main(self.test_args)


cmdclass = versioneer.get_cmdclass()
cmdclass.update({"test": RCMIP})

setup(
    name=PACKAGE_NAME,
    version=versioneer.get_version(),
    description=DESCRIPTION,
    long_description=README_TEXT,
    long_description_content_type="text/x-rst",
    author=", ".join([author[0] for author in AUTHORS]),
    author_email=", ".join([author[1] for author in AUTHORS]),
    url=URL,
    project_urls=PROJECT_URLS,
    license=LICENSE,
    classifiers=CLASSIFIERS,
    keywords=KEYWORDS,
    packages=PACKAGES,
    package_dir=PACKAGE_DIR,
    package_data=PACKAGE_DATA,
    include_package_data=True,
    install_requires=REQUIREMENTS,
    extras_require=REQUIREMENTS_EXTRAS,
    cmdclass=cmdclass,
    entry_points=ENTRY_POINTS,
)
