# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['whetstone']

package_data = \
{'': ['*']}

install_requires = \
['black>=21.7-beta.0,<22.0',
 'oauthlib>=3.1.0,<4.0.0',
 'requests>=2.24.0,<3.0.0',
 'requests_oauthlib>=1.3.0,<2.0.0']

setup_kwargs = {
    'name': 'whetstone',
    'version': '0.4.0',
    'description': '',
    'long_description': None,
    'author': 'Charlie Bini',
    'author_email': 'cbini@kippnj.org',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6.2,<4.0.0',
}


setup(**setup_kwargs)
