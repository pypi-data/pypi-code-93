# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dsxt']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.20,<2.0', 'pandas>=1.2,<2.0', 'scikit-learn==0.24.2']

setup_kwargs = {
    'name': 'dsxt',
    'version': '0.0.3',
    'description': 'Data Science Extensions',
    'long_description': None,
    'author': 'tripl3a',
    'author_email': '34123487+tripl3a@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
