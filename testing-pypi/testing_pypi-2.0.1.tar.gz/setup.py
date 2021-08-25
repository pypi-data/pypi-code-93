# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['testing_pypi']

package_data = \
{'': ['*']}

install_requires = \
['pandas>=1.3.0,<2.0.0']

setup_kwargs = {
    'name': 'testing-pypi',
    'version': '2.0.1',
    'description': 'testing stuff w/ poetry',
    'long_description': '# testing_pypi\nJust to test GitHub actions with poetry\nand PYpI tokens\n',
    'author': 'cbonafin',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/cbonafin',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.1,<4.0.0',
}


setup(**setup_kwargs)
