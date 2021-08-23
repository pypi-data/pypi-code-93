# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fycli',
 'fycli.dependencies',
 'fycli.environment',
 'fycli.infra',
 'fycli.kubernetes',
 'fycli.module',
 'fycli.skeleton',
 'fycli.terraform',
 'fycli.vault']

package_data = \
{'': ['*']}

install_requires = \
['google-cloud-storage>=1.38.0,<2.0.0',
 'pyyaml>=5.3,<6.0',
 'sh>=1.12.14,<2.0.0']

entry_points = \
{'console_scripts': ['fy = fycli.__main__:main']}

setup_kwargs = {
    'name': 'fycli',
    'version': '3.0.0',
    'description': '',
    'long_description': None,
    'author': 'Rob Wilson',
    'author_email': 'roobert@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
