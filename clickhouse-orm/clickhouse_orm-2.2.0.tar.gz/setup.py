# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['clickhouse_orm']

package_data = \
{'': ['*']}

install_requires = \
['iso8601>=0.1.16,<0.2.0', 'pytz>=2021.1,<2022.0', 'requests>=2.26.0,<3.0.0']

setup_kwargs = {
    'name': 'clickhouse-orm',
    'version': '2.2.0',
    'description': 'A simple ORM for working with the Clickhouse database',
    'long_description': None,
    'author': 'olliemath',
    'author_email': 'oliver.margetts@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/SuadeLabs/clickhouse_orm',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6.2,<4',
}


setup(**setup_kwargs)
