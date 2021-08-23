import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "cdk-spot-one",
    "version": "0.6.243",
    "description": "One spot instance with EIP and defined duration. No interruption.",
    "license": "Apache-2.0",
    "url": "https://github.com/pahud/cdk-spot-one.git",
    "long_description_content_type": "text/markdown",
    "author": "Pahud Hsieh<pahudnet@gmail.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/pahud/cdk-spot-one.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "cdk_spot_one",
        "cdk_spot_one._jsii"
    ],
    "package_data": {
        "cdk_spot_one._jsii": [
            "cdk-spot-one@0.6.243.jsii.tgz"
        ],
        "cdk_spot_one": [
            "py.typed"
        ]
    },
    "python_requires": ">=3.6",
    "install_requires": [
        "aws-cdk.aws-ec2>=1.77.0, <2.0.0",
        "aws-cdk.aws-iam>=1.77.0, <2.0.0",
        "aws-cdk.aws-lambda>=1.77.0, <2.0.0",
        "aws-cdk.aws-logs>=1.77.0, <2.0.0",
        "aws-cdk.core>=1.77.0, <2.0.0",
        "aws-cdk.custom-resources>=1.77.0, <2.0.0",
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
    "scripts": [
        "src/cdk_spot_one/_jsii/bin/ec2-connect"
    ]
}
"""
)

with open("README.md", encoding="utf8") as fp:
    kwargs["long_description"] = fp.read()


setuptools.setup(**kwargs)
