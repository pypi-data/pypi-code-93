#!/usr/bin/env python

from setuptools import setup, find_packages

with open("README.md", "r") as readme:
    long_description = readme.read()

setup(
    name="pocar",
    version="0.1",
    description="Process Open Weather data provided by One Call API response.",
    author="Tiago Santos",
    author_email="tiagosarmentosantos@gmail.com",
    url="https://github.com/tiagosarmento/pocar",
    packages=find_packages(exclude=["tests", "tests.*"]),
    long_description=long_description,
    long_description_content_type="text/markdown",
    include_package_data=True,
    install_requires=["DateTime", "requests"],
    python_requires=">=3.6",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
    ],
    package_data={"": ["*.bz2", "*.md", "*.txt", "*.json"]},
    keywords="openweather onecallapi python",
    license="MIT",
)
