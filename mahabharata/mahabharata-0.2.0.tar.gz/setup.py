# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['mahabharata',
 'mahabharata.models',
 'mahabharata.services',
 'mahabharata.services.cli_service',
 'mahabharata.services.poet_service']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.0.1,<9.0.0']

extras_require = \
{':python_version >= "3.7" and python_version < "4.0"': ['pydantic>=1.8.2,<2.0.0'],
 'api': ['gunicorn>=20.1.0,<21.0.0',
         'uvicorn>=0.15.0,<0.16.0',
         'fastapi>=0.68.0,<0.69.0']}

setup_kwargs = {
    'name': 'mahabharata',
    'version': '0.2.0',
    'description': '',
    'long_description': None,
    'author': 'Sharlon Regales',
    'author_email': 'sharlon.regales@tno.nl',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
