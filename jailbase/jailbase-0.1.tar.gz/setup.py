#!/usr/bin/env python3

from setuptools import setup, find_packages

setup(
    name="jailbase",
    version="0.1",
    description="Wrapper to jail base api",
    url="https://github.com/adarshmelethil/jailbase",
    download_url="",
    license="MIT",
    keywords=["crime", "api"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
    ],
    author="Adarsh Melethil",
    author_email="adarshmelethil@gmail.com",
    install_requires=["requests", "docopts", "tabulate"],
    packages=find_packages("src"),
    package_dir={"": "src"},
    entry_points={"console_scripts": ["jailbase=jailbase.cli:main"]},
)
