import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "eks-spot-blocks",
    "version": "0.2.254",
    "description": "A sample JSII construct lib for AWS CDK",
    "license": "Apache-2.0",
    "url": "https://github.com/pahud/cdk-eks-spotblocks.git",
    "long_description_content_type": "text/markdown",
    "author": "Pahud Hsieh<pahudnet@gmail.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/pahud/cdk-eks-spotblocks.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "eks_spot_blocks",
        "eks_spot_blocks._jsii"
    ],
    "package_data": {
        "eks_spot_blocks._jsii": [
            "eks-spot-blocks@0.2.254.jsii.tgz"
        ],
        "eks_spot_blocks": [
            "py.typed"
        ]
    },
    "python_requires": ">=3.6",
    "install_requires": [
        "aws-cdk.aws-ec2>=1.82.0, <2.0.0",
        "aws-cdk.aws-eks>=1.82.0, <2.0.0",
        "aws-cdk.aws-iam>=1.82.0, <2.0.0",
        "aws-cdk.aws-ssm>=1.82.0, <2.0.0",
        "aws-cdk.core>=1.82.0, <2.0.0",
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
