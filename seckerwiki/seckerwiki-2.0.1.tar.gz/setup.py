# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['seckerwiki', 'seckerwiki.commands', 'seckerwiki.scripts']

package_data = \
{'': ['*']}

install_requires = \
['PyInquirer>=1.0.3,<2.0.0',
 'PyYAML>=5.4.1,<6.0.0',
 'pdf2image>=1.16.0,<2.0.0',
 'requests>=2.26.0,<3.0.0']

entry_points = \
{'console_scripts': ['wiki = seckerwiki.wiki:main']}

setup_kwargs = {
    'name': 'seckerwiki',
    'version': '2.0.1',
    'description': 'A collection of scripts used to manage my personal Foam workspace',
    'long_description': None,
    'author': 'Benjamin Secker',
    'author_email': 'benjamin.secker@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/bsecker/wiki/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
