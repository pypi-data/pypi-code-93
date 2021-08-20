import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "cdk-metaflow",
    "version": "0.0.16",
    "description": "A JSII construct library to build Metaflow infrastructure on AWS using Python, Typescript or Go",
    "license": "Apache-2.0",
    "url": "https://github.com/bcgalvin/metaflow-cdk",
    "long_description_content_type": "text/markdown",
    "author": "bcgalvin<bcgalvin@gmail.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/bcgalvin/metaflow-cdk"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "cdk_metaflow",
        "cdk_metaflow._jsii"
    ],
    "package_data": {
        "cdk_metaflow._jsii": [
            "cdk-metaflow@0.0.16.jsii.tgz"
        ],
        "cdk_metaflow": [
            "py.typed"
        ]
    },
    "python_requires": ">=3.6",
    "install_requires": [
        "aws-cdk.aws-apigateway>=1.119.0, <2.0.0",
        "aws-cdk.aws-batch>=1.119.0, <2.0.0",
        "aws-cdk.aws-cloudwatch>=1.119.0, <2.0.0",
        "aws-cdk.aws-dynamodb>=1.119.0, <2.0.0",
        "aws-cdk.aws-ec2>=1.119.0, <2.0.0",
        "aws-cdk.aws-ecs>=1.119.0, <2.0.0",
        "aws-cdk.aws-elasticloadbalancingv2>=1.119.0, <2.0.0",
        "aws-cdk.aws-events>=1.119.0, <2.0.0",
        "aws-cdk.aws-iam>=1.119.0, <2.0.0",
        "aws-cdk.aws-lambda>=1.119.0, <2.0.0",
        "aws-cdk.aws-logs>=1.119.0, <2.0.0",
        "aws-cdk.aws-rds>=1.119.0, <2.0.0",
        "aws-cdk.aws-s3>=1.119.0, <2.0.0",
        "aws-cdk.aws-secretsmanager>=1.119.0, <2.0.0",
        "aws-cdk.aws-ssm>=1.119.0, <2.0.0",
        "aws-cdk.core>=1.119.0, <2.0.0",
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
        "Development Status :: 4 - Beta",
        "License :: OSI Approved"
    ],
    "scripts": []
}
"""
)

with open("README.md", encoding="utf8") as fp:
    kwargs["long_description"] = fp.read()


setuptools.setup(**kwargs)
