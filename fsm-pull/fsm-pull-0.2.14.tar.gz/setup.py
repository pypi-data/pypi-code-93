# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fsm_pull', 'fsm_pull.protobuf']

package_data = \
{'': ['*']}

install_requires = \
['docopt>=0.6.2,<0.7.0',
 'loguru>=0.5.3,<0.6.0',
 'mypy-protobuf>=2.4,<3.0',
 'requests>=2.25.1,<3.0.0',
 'tqdm>=4.62.0,<5.0.0',
 'vivaldi>=0.2.4,<0.3.0']

entry_points = \
{'console_scripts': ['fsm-pull = fsm_pull.fsm:main']}

setup_kwargs = {
    'name': 'fsm-pull',
    'version': '0.2.14',
    'description': 'Tool for downloading data from FSM',
    'long_description': None,
    'author': 'Lohith Anandan',
    'author_email': 'lohith@vernacular.ai',
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
