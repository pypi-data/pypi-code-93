import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "cdk_databrew_cicd",
    "version": "0.1.37",
    "description": "A construct for AWS Glue DataBrew wtih CICD",
    "license": "Apache-2.0",
    "url": "https://github.com/HsiehShuJeng/cdk-databrew-cicd.git",
    "long_description_content_type": "text/markdown",
    "author": "Shu-Jeng Hsieh",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/HsiehShuJeng/cdk-databrew-cicd.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "cdk_databrew_cicd",
        "cdk_databrew_cicd._jsii"
    ],
    "package_data": {
        "cdk_databrew_cicd._jsii": [
            "cdk-databrew-cicd@0.1.37.jsii.tgz"
        ],
        "cdk_databrew_cicd": [
            "py.typed"
        ]
    },
    "python_requires": ">=3.6",
    "install_requires": [
        "aws-cdk.aws-codecommit>=1.113.0, <2.0.0",
        "aws-cdk.aws-codepipeline-actions>=1.113.0, <2.0.0",
        "aws-cdk.aws-codepipeline>=1.113.0, <2.0.0",
        "aws-cdk.aws-iam>=1.113.0, <2.0.0",
        "aws-cdk.aws-lambda>=1.113.0, <2.0.0",
        "aws-cdk.aws-logs>=1.113.0, <2.0.0",
        "aws-cdk.aws-s3>=1.113.0, <2.0.0",
        "aws-cdk.core>=1.113.0, <2.0.0",
        "aws-cdk.custom-resources>=1.113.0, <2.0.0",
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
