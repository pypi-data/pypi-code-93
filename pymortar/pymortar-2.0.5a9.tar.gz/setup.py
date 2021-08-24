# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pymortar']

package_data = \
{'': ['*']}

install_requires = \
['brickschema>=0.4,<0.5',
 'googleapis-common-protos>=1.52.0,<2.0.0',
 'pandas>=1.1,<2.0',
 'pyarrow>=3.0.0,<4.0.0',
 'python-snappy>=0.6.0,<0.7.0',
 'rdflib>=5.0.0,<6.0.0',
 'requests>=2.25.0,<3.0.0',
 'toml>=0.10.2,<0.11.0']

setup_kwargs = {
    'name': 'pymortar',
    'version': '2.0.5a9',
    'description': '',
    'long_description': None,
    'author': 'Gabe Fierro',
    'author_email': 'gtfierro@cs.berkeley.edu',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
