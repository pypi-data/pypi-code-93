# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['poetry_chuy_plugin']

package_data = \
{'': ['*']}

install_requires = \
['chuy==1.2.0', 'poetry>=1.1.7,<2.0.0']

entry_points = \
{'poetry.chuy': ['chuy = poetry_chuy_plugin.plugin:ChuyPlugin']}

setup_kwargs = {
    'name': 'poetry-chuy-plugin',
    'version': '0.1.0',
    'description': 'Plugin to integrate Chuy with Poetry',
    'long_description': None,
    'author': 'Eliaz Bobadilla',
    'author_email': 'eliaz.bobadilladev@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
