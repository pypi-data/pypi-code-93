# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['getools', 'getools.utils']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.18.1,<2.0.0', 'scipy>=1.4.1,<2.0.0']

setup_kwargs = {
    'name': 'getools',
    'version': '0.1.2',
    'description': 'Genetics, Evolution and Bioinformatic tools',
    'long_description': None,
    'author': 'russellmyers',
    'author_email': 'flipside@netspace.net.au',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
