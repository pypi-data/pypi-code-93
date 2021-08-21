#!/usr/bin/env python3
import os

import setuptools

version = {}
with open("elasticsearch_cli/version.py", "r") as f:
    exec(f.read(), version)

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    author="Rivet Health",
    author_email="ops@rivethealth.com",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 2",
    ],
    description="Elasticsearch CLI client",
    entry_points={
        "console_scripts": [
            "es=elasticsearch_cli.cli:main",
        ]
    },
    extras_require={"aws": ["boto3", "requests-aws4auth"], "dev": ["black", "isort"]},
    install_requires=["requests"],
    long_description=long_description,
    long_description_content_type="text/markdown",
    name="relasticsearch-cli",
    packages=setuptools.find_packages(),
    project_urls={
        "Issues": "https://github.com/rivethealth/elasticsearch-cli/issues",
    },
    url="https://github.com/rivethealth/elasticsearch-cli",
    version=version["__version__"],
)
