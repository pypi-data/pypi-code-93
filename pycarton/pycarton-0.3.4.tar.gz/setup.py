# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['carton']

package_data = \
{'': ['*']}

install_requires = \
['pytoml>=0.1.21,<0.2.0', 'ruyaml>=0.20.0,<0.21.0']

setup_kwargs = {
    'name': 'pycarton',
    'version': '0.3.4',
    'description': 'Python toolbox.',
    'long_description': None,
    'author': 'Yevgnen Koh',
    'author_email': 'wherejoystarts@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
