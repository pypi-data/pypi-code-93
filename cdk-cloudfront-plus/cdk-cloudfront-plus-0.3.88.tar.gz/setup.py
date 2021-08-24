import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "cdk-cloudfront-plus",
    "version": "0.3.88",
    "description": "CDK construct library for CloudFront Extensions",
    "license": "Apache-2.0",
    "url": "https://github.com/pahud/cdk-cloudfront-plus.git",
    "long_description_content_type": "text/markdown",
    "author": "Pahud Hsieh<pahudnet@gmail.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/pahud/cdk-cloudfront-plus.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "cdk_cloudfront_plus",
        "cdk_cloudfront_plus._jsii"
    ],
    "package_data": {
        "cdk_cloudfront_plus._jsii": [
            "cdk-cloudfront-plus@0.3.88.jsii.tgz"
        ],
        "cdk_cloudfront_plus": [
            "py.typed"
        ]
    },
    "python_requires": ">=3.6",
    "install_requires": [
        "aws-cdk.aws-apigatewayv2-integrations>=1.73.0, <2.0.0",
        "aws-cdk.aws-apigatewayv2>=1.73.0, <2.0.0",
        "aws-cdk.aws-cloudfront-origins>=1.73.0, <2.0.0",
        "aws-cdk.aws-cloudfront>=1.73.0, <2.0.0",
        "aws-cdk.aws-iam>=1.73.0, <2.0.0",
        "aws-cdk.aws-kinesisfirehose>=1.73.0, <2.0.0",
        "aws-cdk.aws-lambda-nodejs>=1.73.0, <2.0.0",
        "aws-cdk.aws-lambda>=1.73.0, <2.0.0",
        "aws-cdk.aws-s3-deployment>=1.73.0, <2.0.0",
        "aws-cdk.aws-s3>=1.73.0, <2.0.0",
        "aws-cdk.aws-sam>=1.73.0, <2.0.0",
        "aws-cdk.core>=1.73.0, <2.0.0",
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
