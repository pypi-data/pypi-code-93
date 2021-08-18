# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['execution_controller']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'execution-controller',
    'version': '0.1.6',
    'description': 'Модуль инструментов для контроля процесса выполнения python программы',
    'long_description': '# execution-controller\n\nМодуль python для контроля выполнения программы\n',
    'author': 'rocshers',
    'author_email': 'prog.rocshers@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
