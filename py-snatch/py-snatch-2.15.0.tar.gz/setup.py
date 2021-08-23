# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['snatch', 'snatch.base', 'snatch.helpers']

package_data = \
{'': ['*']}

install_requires = \
['arrow',
 'asbool',
 'boto3',
 'loguru',
 'marshmallow',
 'python-dotenv',
 'requests',
 'scalpl',
 'validate-docbr']

setup_kwargs = {
    'name': 'py-snatch',
    'version': '2.15.0',
    'description': "The Friendly Integration Library for Data Scientists. Don't You Just Know It?",
    'long_description': None,
    'author': 'A55 Tech',
    'author_email': 'tech@a55.tech',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
