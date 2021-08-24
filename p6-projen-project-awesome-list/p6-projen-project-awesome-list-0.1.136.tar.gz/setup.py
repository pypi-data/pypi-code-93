import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "p6-projen-project-awesome-list",
    "version": "0.1.136",
    "description": "Projen External Project for awesome-lists",
    "license": "Apache-2.0",
    "url": "https://github.com/p6m7g8/p6-projen-project-awesome-list.git",
    "long_description_content_type": "text/markdown",
    "author": "Philip M. Gollucci<pgollucci@p6m7g8.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/p6m7g8/p6-projen-project-awesome-list.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "p6_projen_project_awesome_list",
        "p6_projen_project_awesome_list._jsii"
    ],
    "package_data": {
        "p6_projen_project_awesome_list._jsii": [
            "p6-projen-project-awesome-list@0.1.136.jsii.tgz"
        ],
        "p6_projen_project_awesome_list": [
            "py.typed"
        ]
    },
    "python_requires": ">=3.6",
    "install_requires": [
        "jsii>=1.33.0, <2.0.0",
        "projen<1.0.0",
        "publication>=0.0.3"
    ],
    "classifiers": [
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Typing :: Typed",
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved"
    ],
    "scripts": []
}
"""
)

with open("README.md", encoding="utf8") as fp:
    kwargs["long_description"] = fp.read()


setuptools.setup(**kwargs)
