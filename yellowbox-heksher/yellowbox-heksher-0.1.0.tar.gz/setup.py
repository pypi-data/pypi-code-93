# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['yellowbox_heksher']

package_data = \
{'': ['*']}

install_requires = \
['httpx', 'yellowbox[postgresql]>=0.6.4']

setup_kwargs = {
    'name': 'yellowbox-heksher',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Biocatch LTD',
    'author_email': 'serverteam@biocatch.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
