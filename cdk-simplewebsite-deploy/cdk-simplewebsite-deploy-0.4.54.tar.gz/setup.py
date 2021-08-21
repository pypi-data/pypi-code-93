import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "cdk-simplewebsite-deploy",
    "version": "0.4.54",
    "description": "This is an AWS CDK Construct to simplify deploying a single-page website use CloudFront distributions.",
    "license": "Apache-2.0",
    "url": "https://github.com/SnapPetal/cdk-simplewebsite-deploy",
    "long_description_content_type": "text/markdown",
    "author": "Thon Becker<thon.becker@gmail.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/SnapPetal/cdk-simplewebsite-deploy"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "cdk_simplewebsite_deploy",
        "cdk_simplewebsite_deploy._jsii"
    ],
    "package_data": {
        "cdk_simplewebsite_deploy._jsii": [
            "cdk-simplewebsite-deploy@0.4.54.jsii.tgz"
        ],
        "cdk_simplewebsite_deploy": [
            "py.typed"
        ]
    },
    "python_requires": ">=3.6",
    "install_requires": [
        "aws-cdk.aws-certificatemanager>=1.119.0, <2.0.0",
        "aws-cdk.aws-cloudfront-origins>=1.119.0, <2.0.0",
        "aws-cdk.aws-cloudfront>=1.119.0, <2.0.0",
        "aws-cdk.aws-route53-targets>=1.119.0, <2.0.0",
        "aws-cdk.aws-route53>=1.119.0, <2.0.0",
        "aws-cdk.aws-s3-deployment>=1.119.0, <2.0.0",
        "aws-cdk.aws-s3>=1.119.0, <2.0.0",
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
