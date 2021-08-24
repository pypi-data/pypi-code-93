# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['unpoly', 'unpoly.contrib']

package_data = \
{'': ['*']}

install_requires = \
['attrs>=21.2.0,<22.0.0']

setup_kwargs = {
    'name': 'unpoly',
    'version': '0.0.1',
    'description': 'Framework agnostic implementation of the unpoly server-protocol.',
    'long_description': None,
    'author': 'Florian Apolloner',
    'author_email': 'florian@apolloner.eu',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6.2,<3.11',
}


setup(**setup_kwargs)
