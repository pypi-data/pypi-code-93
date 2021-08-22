# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['classiq_interface',
 'classiq_interface.analyzer',
 'classiq_interface.backend',
 'classiq_interface.combinatorial_optimization',
 'classiq_interface.combinatorial_optimization.examples',
 'classiq_interface.execute',
 'classiq_interface.finance',
 'classiq_interface.generator',
 'classiq_interface.generator.preferences',
 'classiq_interface.generator.validations',
 'classiq_interface.hybrid',
 'classiq_interface.pyomo_extension',
 'classiq_interface.server']

package_data = \
{'': ['*']}

install_requires = \
['Pyomo>=6.0,<7.0',
 'more-itertools>=8.8.0,<9.0.0',
 'networkx>=2.5.1,<3.0.0',
 'numpy>=1.20.1,<2.0.0',
 'pydantic>=1.8.2,<2.0.0',
 'qiskit>=0.29.0,<0.30.0']

setup_kwargs = {
    'name': 'classiq-interface',
    'version': '0.1.0.1',
    'description': 'Classiq Interface',
    'long_description': 'See [classiq package](https://pypi.org/project/classiq/) README.',
    'author': 'Classiq Technologies',
    'author_email': 'support@classiq.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://classiq.io',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
