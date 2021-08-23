import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "cdk-eksdistro",
    "version": "0.0.141",
    "description": "AWS CDK construct library for Amazon EKS Distro",
    "license": "Apache-2.0",
    "url": "https://github.com/pahud/cdk-eksdistro.git",
    "long_description_content_type": "text/markdown",
    "author": "Pahud Hsieh<pahudnet@gmail.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/pahud/cdk-eksdistro.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "cdk_eksdistro",
        "cdk_eksdistro._jsii"
    ],
    "package_data": {
        "cdk_eksdistro._jsii": [
            "cdk-eksdistro@0.0.141.jsii.tgz"
        ],
        "cdk_eksdistro": [
            "py.typed"
        ]
    },
    "python_requires": ">=3.6",
    "install_requires": [
        "aws-cdk.aws-autoscaling>=1.85.0, <2.0.0",
        "aws-cdk.aws-ec2>=1.85.0, <2.0.0",
        "aws-cdk.aws-iam>=1.85.0, <2.0.0",
        "aws-cdk.core>=1.85.0, <2.0.0",
        "cdk-ec2spot>=0.1.45, <0.2.0",
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
