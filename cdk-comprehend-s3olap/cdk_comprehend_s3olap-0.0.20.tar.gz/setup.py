import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "cdk_comprehend_s3olap",
    "version": "0.0.20",
    "description": "A constrcut for PII and redaction scenarios with Amazon Comprehend and S3 Object Lambda",
    "license": "Apache-2.0",
    "url": "https://github.com/HsiehShuJeng/cdk-comprehend-s3olap.git",
    "long_description_content_type": "text/markdown",
    "author": "Shu-Jeng Hsieh",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/HsiehShuJeng/cdk-comprehend-s3olap.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "cdk_comprehend_s3olap",
        "cdk_comprehend_s3olap._jsii"
    ],
    "package_data": {
        "cdk_comprehend_s3olap._jsii": [
            "cdk-comprehend-s3olap@0.0.20.jsii.tgz"
        ],
        "cdk_comprehend_s3olap": [
            "py.typed"
        ]
    },
    "python_requires": ">=3.6",
    "install_requires": [
        "aws-cdk.aws-iam>=1.112.0, <2.0.0",
        "aws-cdk.aws-lambda-nodejs>=1.112.0, <2.0.0",
        "aws-cdk.aws-lambda>=1.112.0, <2.0.0",
        "aws-cdk.aws-logs>=1.112.0, <2.0.0",
        "aws-cdk.aws-s3-deployment>=1.112.0, <2.0.0",
        "aws-cdk.aws-s3>=1.112.0, <2.0.0",
        "aws-cdk.aws-s3objectlambda>=1.112.0, <2.0.0",
        "aws-cdk.aws-sam>=1.112.0, <2.0.0",
        "aws-cdk.core>=1.112.0, <2.0.0",
        "aws-cdk.custom-resources>=1.112.0, <2.0.0",
        "constructs>=3.2.27, <4.0.0",
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
