import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "affinidi.common-check-widget-backend-lib",
    "version": "1.3.1",
    "description": "An common-check-widget-backend-lib used to development backend for common-check-widget-frontend",
    "license": "MIT-0",
    "url": "https://gitlab.com/affinidi/safe-travel/st-experiments/common-check-widget-backend-lib",
    "long_description_content_type": "text/markdown",
    "author": "Chai Jian Wei <jianwei.c@affinidi.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/affinityproject/common-check-widget-backend-lib.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "affinidi.common_check_widget_backend_lib",
        "affinidi.common_check_widget_backend_lib._jsii",
        "affinidi.common_check_widget_backend_lib.common_check_verify",
        "affinidi.common_check_widget_backend_lib.common_check_verify.endpoint_service_base"
    ],
    "package_data": {
        "affinidi.common_check_widget_backend_lib._jsii": [
            "common-check-widget-backend-lib@1.3.1.jsii.tgz"
        ],
        "affinidi.common_check_widget_backend_lib": [
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
