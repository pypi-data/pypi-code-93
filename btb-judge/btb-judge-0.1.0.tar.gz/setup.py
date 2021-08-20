# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['btb_judge']

package_data = \
{'': ['*']}

install_requires = \
['djangorestframework>=3.12.4,<4.0.0',
 'requests>=2.26.0,<3.0.0',
 'typer[all]>=0.3.2,<0.4.0']

entry_points = \
{'console_scripts': ['btb-judge = btb_judge.main:app']}

setup_kwargs = {
    'name': 'btb-judge',
    'version': '0.1.0',
    'description': 'The judge for Bob The Builder game',
    'long_description': '# Bob The Builder Judge\n\nLocal judge for bob the builder\n',
    'author': 'Shreyansh Murarka',
    'author_email': 'shreyanshmurarka97@gmail.com',
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
