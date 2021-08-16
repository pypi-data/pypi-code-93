import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "affinidi-common-check-widget-backend-lib",
    "version": "1.0.4",
    "description": "An common-check-widget-backend-lib used to development backend for common-check-widget-frontend",
    "license": "MIT-0",
    "url": "https://gitlab.com/affinidi/safe-travel/st-experiments/common-check-widget-backend-lib",
    "long_description_content_type": "text/markdown",
    "author": "Chai Jian Wei<jianwei.c@affinidi.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://gitlab.com/affinidi/safe-travel/st-experiments/common-check-widget-backend-lib.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "affinidi-common-check-widget-backend-lib",
        "affinidi-common-check-widget-backend-lib._jsii"
    ],
    "package_data": {
        "affinidi-common-check-widget-backend-lib._jsii": [
            "common-check-widget-backend-lib@1.0.4.jsii.tgz"
        ],
        "affinidi-common-check-widget-backend-lib": [
            "py.typed"
        ]
    },
    "python_requires": ">=3.6",
    "install_requires": [
        "jsii>=1.32.0, <2.0.0",
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
        "License :: OSI Approved"
    ],
    "scripts": []
}
"""
)

with open("README.md", encoding="utf8") as fp:
    kwargs["long_description"] = fp.read()


setuptools.setup(**kwargs)
