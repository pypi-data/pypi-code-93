# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['django_remove_field']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'django-remove-field',
    'version': '0.2.0',
    'description': 'Handle deletion of django model field without downtime',
    'long_description': None,
    'author': 'Your Name',
    'author_email': 'you@example.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
