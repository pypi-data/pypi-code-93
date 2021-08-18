# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['jointly']

package_data = \
{'': ['*']}

install_requires = \
['matplotlib>=3.4.2,<4.0.0',
 'numpy>=1.21.1,<2.0.0',
 'pandas>=1.3.1,<2.0.0',
 'scipy>=1.7.1,<2.0.0']

setup_kwargs = {
    'name': 'jointly',
    'version': '1.0.0',
    'description': 'Synchronize sensor data from accelerometer shakes',
    'long_description': None,
    'author': 'Ariane Morassi Sasso',
    'author_email': 'ariane.morassi-sasso@hpi.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/hpi-dhc/jointly',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.1,<3.10',
}


setup(**setup_kwargs)
