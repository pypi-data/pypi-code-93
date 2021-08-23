import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "cdk-lambda-bash",
    "version": "0.5.78",
    "description": "Deploy Bash Lambda Functions with AWS CDK",
    "license": "Apache-2.0",
    "url": "https://github.com/pahud/cdk-lambda-bash.git",
    "long_description_content_type": "text/markdown",
    "author": "Pahud Hsieh",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/pahud/cdk-lambda-bash.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "cdk_lambda_bash",
        "cdk_lambda_bash._jsii"
    ],
    "package_data": {
        "cdk_lambda_bash._jsii": [
            "cdk-lambda-bash@0.5.78.jsii.tgz"
        ],
        "cdk_lambda_bash": [
            "py.typed"
        ]
    },
    "python_requires": ">=3.6",
    "install_requires": [
        "aws-cdk.aws-iam>=1.93.0, <2.0.0",
        "aws-cdk.aws-lambda>=1.93.0, <2.0.0",
        "aws-cdk.aws-logs>=1.93.0, <2.0.0",
        "aws-cdk.core>=1.93.0, <2.0.0",
        "aws-cdk.custom-resources>=1.93.0, <2.0.0",
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
