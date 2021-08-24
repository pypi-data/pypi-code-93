import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "cdk-notify-bucket",
    "version": "0.0.28",
    "description": "Create the S3 Bucket, will send event to email when object created",
    "license": "Apache-2.0",
    "url": "https://github.com/neilkuan/cdk-notify-bucket.git",
    "long_description_content_type": "text/markdown",
    "author": "Neil Kuan<guan840912@gmail.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/neilkuan/cdk-notify-bucket.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "cdk_notify_bucket",
        "cdk_notify_bucket._jsii"
    ],
    "package_data": {
        "cdk_notify_bucket._jsii": [
            "cdk-notify-bucket@0.0.28.jsii.tgz"
        ],
        "cdk_notify_bucket": [
            "py.typed"
        ]
    },
    "python_requires": ">=3.6",
    "install_requires": [
        "aws-cdk.aws-iam>=1.115.0, <2.0.0",
        "aws-cdk.aws-s3-notifications>=1.115.0, <2.0.0",
        "aws-cdk.aws-s3>=1.115.0, <2.0.0",
        "aws-cdk.aws-sns>=1.115.0, <2.0.0",
        "aws-cdk.core>=1.115.0, <2.0.0",
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
