# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['awyes']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=5.4.1,<6.0.0',
 'boto3>=1.17.62,<2.0.0',
 'docker>=5.0.0,<6.0.0',
 'requests>=2.25.1,<3.0.0']

entry_points = \
{'console_scripts': ['deploy = awyes.deployment:deploy']}

setup_kwargs = {
    'name': 'awyes',
    'version': '2.1.14',
    'description': 'Simplify aws deployment',
    'long_description': None,
    'author': 'trumanpurnell',
    'author_email': 'truman.purnell@gmail.com',
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
