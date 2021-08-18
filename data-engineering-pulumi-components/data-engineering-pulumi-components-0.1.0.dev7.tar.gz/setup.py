# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['data_engineering_pulumi_components',
 'data_engineering_pulumi_components.aws',
 'data_engineering_pulumi_components.aws.lambda_.copy_',
 'data_engineering_pulumi_components.aws.lambda_.move',
 'data_engineering_pulumi_components.aws.lambda_.validate',
 'data_engineering_pulumi_components.pipelines']

package_data = \
{'': ['*']}

install_requires = \
['boto3>=1.17.00,<2.0.0', 'pulumi-aws>=4.0.0,<5.0.0', 'pulumi>=3.0.0,<4.0.0']

setup_kwargs = {
    'name': 'data-engineering-pulumi-components',
    'version': '0.1.0.dev7',
    'description': 'Reusable components for use in Pulumi Python projects',
    'long_description': None,
    'author': 'MoJ Data Engineering Team',
    'author_email': 'data-engineering@digital.justice.gov.uk',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
