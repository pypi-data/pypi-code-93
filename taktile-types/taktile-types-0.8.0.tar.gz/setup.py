# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['taktile_types',
 'taktile_types.enums',
 'taktile_types.enums.repository',
 'taktile_types.schemas',
 'taktile_types.schemas.deployment',
 'taktile_types.schemas.repository']

package_data = \
{'': ['*']}

install_requires = \
['pydantic>=1.8.2,<2.0.0']

setup_kwargs = {
    'name': 'taktile-types',
    'version': '0.8.0',
    'description': '',
    'long_description': None,
    'author': 'Taktile GmbH',
    'author_email': 'devops@taktile.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
