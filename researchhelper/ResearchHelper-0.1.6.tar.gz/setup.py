# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['researchhelper',
 'researchhelper.analyse',
 'researchhelper.datastructures',
 'researchhelper.decorators',
 'researchhelper.modeling',
 'researchhelper.optimize',
 'researchhelper.processdata',
 'researchhelper.visualize']

package_data = \
{'': ['*']}

install_requires = \
['matplotlib>=3.4.0,<4.0.0',
 'networkx>=2.6.2,<3.0.0',
 'numpy>=1.20.1,<2.0.0',
 'pydantic>=1.8.2,<2.0.0',
 'scipy>=1.6.2,<2.0.0',
 'tqdm>=4.62.1,<5.0.0']

setup_kwargs = {
    'name': 'researchhelper',
    'version': '0.1.6',
    'description': '',
    'long_description': None,
    'author': 'Bas Chatel',
    'author_email': 'bastiaan.chatel@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
