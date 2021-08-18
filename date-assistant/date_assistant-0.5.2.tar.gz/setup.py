# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['date_assistant']

package_data = \
{'': ['*']}

install_requires = \
['python-dateutil>=2.8.2,<3.0.0']

setup_kwargs = {
    'name': 'date-assistant',
    'version': '0.5.2',
    'description': '',
    'long_description': '# Date Assistant\n',
    'author': 'Jorge Alvarado',
    'author_email': 'alvaradosegurajorge@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/jalvaradosegura/date_assistant',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
