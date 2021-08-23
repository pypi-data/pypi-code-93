# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['time_tracker']

package_data = \
{'': ['*']}

install_requires = \
['python-dotenv>=0.12.0,<0.13.0', 'typer>=0.1.0,<0.2.0']

entry_points = \
{'console_scripts': ['tt = time_tracker.main:app']}

setup_kwargs = {
    'name': 'time-tracker',
    'version': '0.1.2',
    'description': '',
    'long_description': '# time-tracker',
    'author': 'Jose Cabeda',
    'author_email': 'jecabeda@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
