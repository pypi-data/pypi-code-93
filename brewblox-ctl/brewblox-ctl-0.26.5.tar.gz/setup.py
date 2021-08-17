# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['brewblox_ctl', 'brewblox_ctl.commands']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=5.4.1,<6.0.0',
 'click>=8.0.1,<9.0.0',
 'configobj>=5.0.6,<6.0.0',
 'docker-compose>=1.29.2,<2.0.0',
 'docker>=5.0.0,<6.0.0',
 'python-dotenv[cli]>=0.19.0,<0.20.0',
 'requests>=2.26.0,<3.0.0',
 'zeroconf>=0.33.1,<0.34.0']

entry_points = \
{'console_scripts': ['brewblox-ctl = brewblox_ctl.__main__:main']}

setup_kwargs = {
    'name': 'brewblox-ctl',
    'version': '0.26.5',
    'description': 'Brewblox management tool',
    'long_description': '# BrewBlox CLI management tool\n\nThe primary tool for installing and managing BrewBlox. Uses Click.\n\nInstall-specific commands are defined in [brewblox-ctl-lib](https://github.com/BrewBlox/brewblox-ctl-lib).\n\nWraps multiple docker-compose commands to provide a one-stop tool.\n\nProvides the `http` CLI utility tool as a more specific and less cryptic alternative to `curl`.\n',
    'author': 'BrewPi',
    'author_email': 'development@brewpi.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4',
}


setup(**setup_kwargs)
