# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['tno_poet_press']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'tno-poet-press',
    'version': '0.6.0',
    'description': '',
    'long_description': None,
    'author': 'Sharlon Regales',
    'author_email': 'sharlon.regales@tno.nl',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
