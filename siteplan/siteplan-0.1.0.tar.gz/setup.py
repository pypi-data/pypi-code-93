# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['siteplan']

package_data = \
{'': ['*']}

install_requires = \
['Django>=3.2.6,<4.0.0',
 'click>=8.0.1,<9.0.0',
 'gunicorn>=20.1.0,<21.0.0',
 'whitenoise>=5.3.0,<6.0.0']

entry_points = \
{'console_scripts': ['siteplan = siteplan.cli:main']}

setup_kwargs = {
    'name': 'siteplan',
    'version': '0.1.0',
    'description': 'Quickly build django website',
    'long_description': '\n\nA new way to Django development. Start small, grow big.\n',
    'author': 'Kamal Mustafa',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
