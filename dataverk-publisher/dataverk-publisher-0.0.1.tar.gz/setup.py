# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['dataverk_publisher',
 'dataverk_publisher.connectors',
 'dataverk_publisher.connectors.resources',
 'dataverk_publisher.utils']

package_data = \
{'': ['*']}

install_requires = \
['deetly>=0.0.25,<0.0.26',
 'google-cloud-storage>=1.40.0,<2.0.0',
 'requests>=2.24.0,<3.0.0']

setup_kwargs = {
    'name': 'dataverk-publisher',
    'version': '0.0.1',
    'description': '',
    'long_description': None,
    'author': 'erikvatt',
    'author_email': 'erik.vattekar@nav.no',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
