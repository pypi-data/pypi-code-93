#!/usr/bin/env python
from setuptools import setup, find_packages

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="prunner",
    version="0.4.1",
    author="Moises Baltazar Garcia",
    author_email="me@moisesb.com",
    description="Runs pipelines configured in YAML",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mobalt/pipeline-runner",
    packages=find_packages(),
    # packages=["pipeline"],
    python_requires=">=3.5",
    install_requires=["PyYAML", "Jinja2"],
    entry_points={
        "console_scripts": [
            "prunner = prunner.main:main",
        ],
    },
    keywords="prunner",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: System Administrators",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 3",
        "Topic :: System :: Systems Administration",
        "Topic :: Software Development :: Build Tools",
    ],
    test_suite="tests",
    tests_require=["pytest"],
)
