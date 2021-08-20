# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['django_rlogging',
 'rlogging',
 'rlogging.controllers',
 'rlogging.entities',
 'rlogging.entities.base',
 'rlogging.entities.handlers',
 'rlogging.entities.printers',
 'rlogging.setup']

package_data = \
{'': ['*']}

install_requires = \
['execution-controller']

setup_kwargs = {
    'name': 'rlogging',
    'version': '0.3.4',
    'description': 'Модуль гибкого логирования python приложений',
    'long_description': '# rlogging\n\nМодуль для логирования приложений python',
    'author': 'rocshers',
    'author_email': 'prog.rocshers@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
