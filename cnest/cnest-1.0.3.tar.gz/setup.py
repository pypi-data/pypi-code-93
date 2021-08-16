# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cnest']

package_data = \
{'': ['*']}

install_requires = \
['pybind11>=2.6.2,<3.0.0']

setup_kwargs = {
    'name': 'cnest',
    'version': '1.0.3',
    'description': "An efficient library providing operators on Python's nested data structures, implemented in C++",
    'long_description': "# cnest\n\nAn efficient library providing operators on Python's nested data structures. It includes C++ implementation of several key nest functions that are performance critical.\n\nThis library is developed by [Haonan Yu](https://github.com/hnyu) and alf contributors.\n",
    'author': 'Haonan Yu',
    'author_email': 'haonan.yu@horizon.ai',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}
from build import *
build(setup_kwargs)

setup(**setup_kwargs)
