import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "cdk8s-aws-lb-controller-api-object",
    "version": "0.0.2",
    "description": "@opencdk8s/cdk8s-aws-lb-controller-api-object",
    "license": "Apache-2.0",
    "url": "https://github.com/opencdk8s/cdk8s-aws-lb-controller-api-object",
    "long_description_content_type": "text/markdown",
    "author": "Hunter Thompson<aatman@auroville.org.in>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/opencdk8s/cdk8s-aws-lb-controller-api-object"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "cdk8s_aws_lb_controller_api_object",
        "cdk8s_aws_lb_controller_api_object._jsii"
    ],
    "package_data": {
        "cdk8s_aws_lb_controller_api_object._jsii": [
            "cdk8s-aws-lb-controller-api-object@0.0.2.jsii.tgz"
        ],
        "cdk8s_aws_lb_controller_api_object": [
            "py.typed"
        ]
    },
    "python_requires": ">=3.6",
    "install_requires": [
        "cdk8s-plus-17>=1.0.0.b50, <2.0.0",
        "cdk8s>=1.0.0.b27, <2.0.0",
        "constructs>=3.3.120, <4.0.0",
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
