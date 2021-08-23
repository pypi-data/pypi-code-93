#!/usr/bin/env python

"""The setup script."""
import sys
from setuptools import setup, find_packages

with open("README.rst") as readme_file:
    readme = readme_file.read()

with open("HISTORY.rst") as history_file:
    history = history_file.read()

requirements = ["jinja2", "pydantic", "pactman", "python-slugify"]

# Install typing_extensions on Python 3.7
if sys.version_info < (3, 8):
    requirements.append("typing-extensions")

test_requirements = [
    "pytest>=3",
]

setup(
    author="Chris Lawlor",
    author_email="chris@pymetrics.com",
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    description="Generate Python test cases from Pact files, "
    "for easier provider verification.",
    entry_points={
        "console_scripts": [
            "pact-testgen=pact_testgen.cli:main",
        ],
    },
    install_requires=requirements,
    license="MIT license",
    long_description=readme + "\n\n" + history,
    include_package_data=True,
    keywords="pact_testgen",
    name="pact_testgen",
    packages=find_packages(include=["pact_testgen", "pact_testgen.*"]),
    test_suite="tests",
    tests_require=test_requirements,
    url="https://github.com/pymetrics/pact-testgen",
    version="0.1.0",
    zip_safe=False,
)
