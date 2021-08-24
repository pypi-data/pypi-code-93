# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mutate_function']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'mutate-function',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'mark-todd',
    'author_email': 'markpeter.todd@hotmail.co.uk',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
