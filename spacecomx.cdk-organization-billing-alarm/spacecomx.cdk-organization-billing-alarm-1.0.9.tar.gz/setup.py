import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "spacecomx.cdk-organization-billing-alarm",
    "version": "1.0.9",
    "description": "Multi-account CDK construct to monitor estimated billing charges with alerts and notifications for a AWS Organization. It gives you the capability to monitor specific AWS Service charges, by a linked AWS account in a master/payer account",
    "license": "MIT",
    "url": "https://github.com/spacecomx/cdk-organization-billing-alarm.git",
    "long_description_content_type": "text/markdown",
    "author": "Wayne Gibson<wayne.gibson@spacecomx.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/spacecomx/cdk-organization-billing-alarm.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "spacecomx.cdk_organization_billing-alarm",
        "spacecomx.cdk_organization_billing-alarm._jsii"
    ],
    "package_data": {
        "spacecomx.cdk_organization_billing-alarm._jsii": [
            "cdk-organization-billing-alarm@1.0.9.jsii.tgz"
        ],
        "spacecomx.cdk_organization_billing-alarm": [
            "py.typed"
        ]
    },
    "python_requires": ">=3.6",
    "install_requires": [
        "aws-cdk.aws-secretsmanager>=1.119.0, <2.0.0",
        "aws-cdk.aws-sns>=1.119.0, <2.0.0",
        "aws-cdk.core>=1.119.0, <2.0.0",
        "constructs>=3.2.27, <4.0.0",
        "jsii>=1.33.0, <2.0.0",
        "publication>=0.0.3",
        "spacecomx.cdk-billing-alarm>=1.0.11, <2.0.0"
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
