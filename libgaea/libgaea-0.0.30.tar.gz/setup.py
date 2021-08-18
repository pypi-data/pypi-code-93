# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['gaea', 'gaea.__web__']

package_data = \
{'': ['*'], 'gaea.__web__': ['static/*', 'templates/*']}

install_requires = \
['PySide6>=6.1.2,<7.0.0',
 'feedparser>=6.0.8,<7.0.0',
 'pendulum>=2.1.2,<3.0.0',
 'semver>=2.13.0,<3.0.0',
 'sh>=1.14.2,<2.0.0',
 'understory']

entry_points = \
{'console_scripts': ['build_linux = gaea:build_linux',
                     'build_macos = gaea:build_macos',
                     'build_windows = gaea:build_windows'],
 'web.apps': ['gaea = gaea.__web__:app']}

setup_kwargs = {
    'name': 'libgaea',
    'version': '0.0.30',
    'description': 'Spawner of the understory',
    'long_description': '# gaea\nSpawn and manage your personal websites\n\nDownload and run the most recent [release](https://github.com/canopy/gaea/releases)\nfor your operating system.\n',
    'author': 'Angelo Gladding',
    'author_email': 'self@angelogladding.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<3.10',
}


setup(**setup_kwargs)
