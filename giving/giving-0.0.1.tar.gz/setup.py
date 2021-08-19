# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['giving']

package_data = \
{'': ['*']}

install_requires = \
['Rx>=3.2.0,<4.0.0', 'varname>=0.8.0,<0.9.0']

setup_kwargs = {
    'name': 'giving',
    'version': '0.0.1',
    'description': 'Reactive logging',
    'long_description': None,
    'author': 'Olivier Breuleux',
    'author_email': 'breuleux@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
