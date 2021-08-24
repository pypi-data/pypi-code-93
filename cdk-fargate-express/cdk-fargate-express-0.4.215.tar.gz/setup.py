import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "cdk-fargate-express",
    "version": "0.4.215",
    "description": "A sample JSII construct lib for Express Apps in AWS Fargate",
    "license": "Apache-2.0",
    "url": "https://github.com/pahud/cdk-fargate-express.git",
    "long_description_content_type": "text/markdown",
    "author": "Pahud Hsieh<pahudnet@gmail.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/pahud/cdk-fargate-express.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "cd_fargate_express",
        "cd_fargate_express._jsii"
    ],
    "package_data": {
        "cd_fargate_express._jsii": [
            "cdk-fargate-express@0.4.215.jsii.tgz"
        ],
        "cd_fargate_express": [
            "py.typed"
        ]
    },
    "python_requires": ">=3.6",
    "install_requires": [
        "aws-cdk.aws-ec2>=1.79.0, <2.0.0",
        "aws-cdk.aws-ecs-patterns>=1.79.0, <2.0.0",
        "aws-cdk.aws-ecs>=1.79.0, <2.0.0",
        "aws-cdk.core>=1.79.0, <2.0.0",
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
