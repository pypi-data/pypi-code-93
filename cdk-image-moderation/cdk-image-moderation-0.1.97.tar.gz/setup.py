import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "cdk-image-moderation",
    "version": "0.1.97",
    "description": "Event-driven image moderation and notification with AWS CDK",
    "license": "Apache-2.0",
    "url": "https://github.com/pahud/cdk-image-moderation.git",
    "long_description_content_type": "text/markdown",
    "author": "Pahud Hsieh<pahudnet@gmail.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/pahud/cdk-image-moderation.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "cdk_image_moderation",
        "cdk_image_moderation._jsii"
    ],
    "package_data": {
        "cdk_image_moderation._jsii": [
            "cdk-image-moderation@0.1.97.jsii.tgz"
        ],
        "cdk_image_moderation": [
            "py.typed"
        ]
    },
    "python_requires": ">=3.6",
    "install_requires": [
        "aws-cdk.aws-iam>=1.95.2, <2.0.0",
        "aws-cdk.aws-lambda-nodejs>=1.95.2, <2.0.0",
        "aws-cdk.aws-lambda>=1.95.2, <2.0.0",
        "aws-cdk.aws-s3-notifications>=1.95.2, <2.0.0",
        "aws-cdk.aws-s3>=1.95.2, <2.0.0",
        "aws-cdk.aws-sns-subscriptions>=1.95.2, <2.0.0",
        "aws-cdk.aws-sns>=1.95.2, <2.0.0",
        "aws-cdk.core>=1.95.2, <2.0.0",
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
