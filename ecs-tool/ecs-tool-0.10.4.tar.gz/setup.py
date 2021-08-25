# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ecs_tool',
 'ecs_tool.plugins',
 'ecs_tool.plugins.cluster',
 'ecs_tool.plugins.dashboard',
 'ecs_tool.plugins.service',
 'ecs_tool.plugins.task']

package_data = \
{'': ['*']}

install_requires = \
['arrow>=1.1.0,<2.0.0',
 'asciiplot>=0.1.1,<0.2.0',
 'boto3>=1.9,<2.0',
 'click-log>=0.3.2,<0.4.0',
 'click>=8.0,<9.0',
 'loguru>=0.5.3,<0.6.0',
 'rich>=10.3.0,<11.0.0']

entry_points = \
{'console_scripts': ['ecs = ecs_tool.cli:safe_cli']}

setup_kwargs = {
    'name': 'ecs-tool',
    'version': '0.10.4',
    'description': 'ecs-tool tries to eliminate common caveats for your day-to-day work with Elastic Container Service (ECS).',
    'long_description': '# PROJECT MOVED\nProject moved to https://github.com/whisller/lucyna This repository is kept as read only\n',
    'author': 'Daniel Ancuta',
    'author_email': 'whisller@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/whisller/ecs-tool',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
