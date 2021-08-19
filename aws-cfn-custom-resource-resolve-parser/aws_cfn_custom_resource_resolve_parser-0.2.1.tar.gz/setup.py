# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['aws_cfn_custom_resource_resolve_parser']

package_data = \
{'': ['*']}

install_requires = \
['boto3>=1.18.0,<2.0.0']

setup_kwargs = {
    'name': 'aws-cfn-custom-resource-resolve-parser',
    'version': '0.2.1',
    'description': 'AWS CFN Custom Resource parser for dynamic values',
    'long_description': '======================================\nAWS CFN Custom resource Resolve parser\n======================================\n\n\n.. image:: https://img.shields.io/pypi/v/aws_cfn_custom_resource_resolve_parser.svg\n        :target: https://pypi.python.org/pypi/aws_cfn_custom_resource_resolve_parser\n\n.. image:: https://readthedocs.org/projects/aws-cfn-custom-resource-resolve-parser/badge/?version=latest\n        :target: https://aws-cfn-custom-resource-resolve-parser.readthedocs.io/en/latest/?version=latest\n        :alt: Documentation Status\n\n\n----------------------------------------------------------------------------------------------------\nSmall lib to parse and retrieve secret from AWS Secrets manager using the CFN resolve format string\n----------------------------------------------------------------------------------------------------\n\nIntent\n=======\n\nCurrently in AWS CloudFormation, using **{{resolve}}** does not work for custom resources. Pending the feature being\nreleased, when the use of private resource types is not possible for the use-case, this small lib aims to allow\nparsing secrets so that you can today write your CFN templates with resolve.\n\nRequirements\n=============\n\nSadly, this means the lambda function using this library will still need IAM access directly, and cannot use the role\nused by CloudFormation on create/update currently.\n\nUsage\n=======\n\n.. code-block:: python\n\n    from aws_cfn_custom_resource_resolve_parser import handle\n    secret_string = r"{{resolve:secretsmanager:mysecret:SecretString:password}}"\n    secret_value = handle(secret_string)\n\n\n* Documentation: https://aws-cfn-custom-resource-resolve-parser.readthedocs.io.\n\nCredits\n-------\n\nThis package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.\n\n.. _Cookiecutter: https://github.com/audreyr/cookiecutter\n.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage\n',
    'author': 'John Preston',
    'author_email': 'john@ews-network.net',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
