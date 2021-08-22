# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ecs_composex_specs']

package_data = \
{'': ['*']}

install_requires = \
['jsonschema>=3.2.0,<4.0.0']

setup_kwargs = {
    'name': 'ecs-composex-specs',
    'version': '0.2.9',
    'description': 'JSON Schema Specifications for ECS Compose-X',
    'long_description': '===================\nECS Compose-X Specs\n===================\n\n`Specifications for ECS Compose-X.`_\n\nVisit the `Compose-X repositories on GitHub`_, `use-cases walkthroughs`_ and the `blog`_\n\n.. _Specifications for ECS Compose-X.: https://ecs-composex-specs.compose-x.io\n.. _Compose-X repositories on GitHub: https://github.com/compose-x\n.. _use-cases walkthroughs: https://labs.compose-x.io\n.. _blog: https://blog.compose-x.io\n',
    'author': 'John Preston',
    'author_email': 'john@compose-x.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
