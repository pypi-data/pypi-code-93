# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mumoco', 'mumoco.conanbuilder']

package_data = \
{'': ['*']}

install_requires = \
['cli-ui>=0.14.1,<0.15.0', 'conan>=1.36.0,<2.0.0', 'deserialize>=1.8.1,<2.0.0']

entry_points = \
{'console_scripts': ['mumoco = mumoco.main:main']}

setup_kwargs = {
    'name': 'mumoco',
    'version': '0.3.1',
    'description': 'This is tool helps to work with multiple conan modules simultaneously.',
    'long_description': None,
    'author': 'michel',
    'author_email': 'michel.meyer@disroop.ch',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/disroop/mumoco',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
