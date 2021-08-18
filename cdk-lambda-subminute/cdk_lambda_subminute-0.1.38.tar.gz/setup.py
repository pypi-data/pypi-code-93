import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "cdk_lambda_subminute",
    "version": "0.1.38",
    "description": "A construct for deploying a Lambda function that can be invoked every time unit less than one minute.",
    "license": "Apache-2.0",
    "url": "https://github.com/HsiehShuJeng/cdk-lambda-subminute.git",
    "long_description_content_type": "text/markdown",
    "author": "Shu-Jeng Hsieh",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/HsiehShuJeng/cdk-lambda-subminute.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "cdk_lambda_subminute",
        "cdk_lambda_subminute._jsii"
    ],
    "package_data": {
        "cdk_lambda_subminute._jsii": [
            "cdk-lambda-subminute@0.1.38.jsii.tgz"
        ],
        "cdk_lambda_subminute": [
            "py.typed"
        ]
    },
    "python_requires": ">=3.6",
    "install_requires": [
        "aws-cdk.aws-events-targets>=1.111.0, <2.0.0",
        "aws-cdk.aws-events>=1.111.0, <2.0.0",
        "aws-cdk.aws-iam>=1.111.0, <2.0.0",
        "aws-cdk.aws-lambda-nodejs>=1.111.0, <2.0.0",
        "aws-cdk.aws-lambda>=1.111.0, <2.0.0",
        "aws-cdk.aws-logs>=1.111.0, <2.0.0",
        "aws-cdk.aws-stepfunctions-tasks>=1.111.0, <2.0.0",
        "aws-cdk.aws-stepfunctions>=1.111.0, <2.0.0",
        "aws-cdk.core>=1.111.0, <2.0.0",
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
