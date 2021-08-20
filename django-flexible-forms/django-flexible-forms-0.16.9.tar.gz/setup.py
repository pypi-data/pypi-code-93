# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['flexible_forms']

package_data = \
{'': ['*'], 'flexible_forms': ['static/flexible_forms/admin/*']}

install_requires = \
['django>=2.2',
 'jmespath>=0.10.0,<0.11.0',
 'requests>=2.24.0,<3.0.0',
 'simpleeval>=0.9.10,<0.10.0']

extras_require = \
{':python_version < "3.8"': ['importlib-metadata']}

setup_kwargs = {
    'name': 'django-flexible-forms',
    'version': '0.16.9',
    'description': 'A reusable Django app for managing database-backed forms.',
    'long_description': None,
    'author': 'Eric Abruzzese',
    'author_email': 'eric.abruzzese@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.6.2,<4.0.0',
}


setup(**setup_kwargs)
