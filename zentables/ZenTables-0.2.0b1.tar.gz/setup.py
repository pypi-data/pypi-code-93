# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['zentables']

package_data = \
{'': ['*'], 'zentables': ['templates/*']}

install_requires = \
['Jinja2>=3.0.1,<4.0.0', 'pandas>=1.3.0,<2.0.0']

setup_kwargs = {
    'name': 'zentables',
    'version': '0.2.0b1',
    'description': 'Stress-free descriptive tables in Python.',
    'long_description': None,
    'author': 'Paul Xu',
    'author_email': 'yang_xu@brown.edu',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
