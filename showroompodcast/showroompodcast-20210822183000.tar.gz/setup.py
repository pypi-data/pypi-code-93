#!/usr/bin/env python
"""The setup script."""

from setuptools import find_packages, setup  # type: ignore

with open("README.md", encoding="utf-8") as readme_file:
    readme = readme_file.read()

setup(
    author="Master",
    author_email="roadmasternavi@gmail.com",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content :: Content Management System",
        "Topic :: Multimedia",
        "Topic :: Multimedia :: Video",
        "Topic :: Multimedia :: Video :: Capture",
        "Topic :: System",
        "Topic :: System :: Archiving",
        "Topic :: System :: Archiving :: Backup",
        "Topic :: System :: Monitoring",
        "Topic :: System :: Networking",
        "Topic :: System :: Networking :: Monitoring",
        "Typing :: Typed",
    ],
    dependency_links=[],
    description="Automatic archiver for SHOWROOM live which is listed by YAML file.",  # noqa: E501 pylint: disable=line-too-long
    entry_points={"console_scripts": ["showroom-podcast=showroompodcast.cli:showroom_podcast"]},
    exclude_package_data={"": ["__pycache__", "*.py[co]", ".pytest_cache"]},
    include_package_data=True,
    install_requires=["asynccpu", "asyncffmpeg", "click>=7.0", "slack-sdk", "yamldataclassconfig"],
    keywords="archive showroom",
    long_description=readme,
    long_description_content_type="text/markdown",
    name="showroompodcast",
    packages=find_packages(include=["showroompodcast", "showroompodcast.*"]),
    package_data={"showroompodcast": ["py.typed"]},
    python_requires=">=3.9",
    test_suite="tests",
    tests_require=["pytest>=3"],
    url="https://github.com/road-master/showroom-podcast",
    version="20210822183000",
    zip_safe=False,
)
