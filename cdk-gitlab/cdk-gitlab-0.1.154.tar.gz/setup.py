import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "cdk-gitlab",
    "version": "0.1.154",
    "description": "High level CDK construct to provision GitLab integrations with AWS",
    "license": "Apache-2.0",
    "url": "https://github.com/pahud/cdk-gitlab.git",
    "long_description_content_type": "text/markdown",
    "author": "Pahud Hsieh<pahudnet@gmail.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/pahud/cdk-gitlab.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "cdk_gitlab",
        "cdk_gitlab._jsii"
    ],
    "package_data": {
        "cdk_gitlab._jsii": [
            "cdk-gitlab@0.1.154.jsii.tgz"
        ],
        "cdk_gitlab": [
            "py.typed"
        ]
    },
    "python_requires": ">=3.6",
    "install_requires": [
        "aws-cdk.aws-ec2>=1.82.0, <2.0.0",
        "aws-cdk.aws-ecs>=1.82.0, <2.0.0",
        "aws-cdk.aws-eks>=1.82.0, <2.0.0",
        "aws-cdk.aws-iam>=1.82.0, <2.0.0",
        "aws-cdk.core>=1.82.0, <2.0.0",
        "constructs>=3.2.27, <4.0.0",
        "jsii>=1.33.0, <2.0.0",
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
