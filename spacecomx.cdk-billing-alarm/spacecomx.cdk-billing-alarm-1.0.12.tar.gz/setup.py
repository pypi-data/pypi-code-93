import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "spacecomx.cdk-billing-alarm",
    "version": "1.0.12",
    "description": "It sets up an estimated monthly billing alarm associated with an email address endpoint. It then subscribes that endpoint to an SNS Topic created by the package or it can use an existing SNS Topic Arn. The CDK construct can be used to implement multiple customizable billing alarms for single or master/payer account e.g (AWS Organization).",
    "license": "MIT",
    "url": "https://github.com/spacecomx/cdk-billing-alarm.git",
    "long_description_content_type": "text/markdown",
    "author": "Wayne Gibson<wayne.gibson@spacecomx.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/spacecomx/cdk-billing-alarm.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "spacecomx.cdk_billing_alarm",
        "spacecomx.cdk_billing_alarm._jsii"
    ],
    "package_data": {
        "spacecomx.cdk_billing_alarm._jsii": [
            "cdk-billing-alarm@1.0.12.jsii.tgz"
        ],
        "spacecomx.cdk_billing_alarm": [
            "py.typed"
        ]
    },
    "python_requires": ">=3.6",
    "install_requires": [
        "aws-cdk.aws-cloudwatch-actions>=1.119.0, <2.0.0",
        "aws-cdk.aws-cloudwatch>=1.119.0, <2.0.0",
        "aws-cdk.aws-sns-subscriptions>=1.119.0, <2.0.0",
        "aws-cdk.aws-sns>=1.119.0, <2.0.0",
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
