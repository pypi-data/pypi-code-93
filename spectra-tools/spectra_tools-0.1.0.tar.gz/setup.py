# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['spectra_tools', 'spectra_tools.nmr', 'spectra_tools.nmr.tree']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'spectra-tools',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Steven Bennett',
    'author_email': 's.bennett18@imperial.ac.uk',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
