# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['badgey']

package_data = \
{'': ['*']}

install_requires = \
['GitPython>=3.1.20,<4.0.0',
 'docopt>=0.6.2,<0.7.0',
 'matplotlib>=3.4.3,<4.0.0',
 'pybadges>=2.2.1,<3.0.0']

entry_points = \
{'console_scripts': ['badgey = badgey:main']}

setup_kwargs = {
    'name': 'badgey',
    'version': '0.2.2',
    'description': 'A library and a CLI to locally generate project badges',
    'long_description': '# Badgey\n[![pipeline status](https://gitlab.com/rubendibattista/badgey/badges/master/pipeline.svg)](https://gitlab.com/rubendibattista/badgey/commits/master)\n[![loc](https://gitlab.com/rubendibattista/badgey/-/jobs/artifacts/master/raw/loc.svg?job=badges)](https://gitlab.com/rubendibattista/badgey/master)\n[![version](https://gitlab.com/rubendibattista/badgey/-/jobs/artifacts/master/raw/version.svg?job=badges)](https://gitlab.com/rubendibattista/badgey/-/releases)\n\n',
    'author': 'Ruben Di Battista',
    'author_email': 'rubendibattista@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
