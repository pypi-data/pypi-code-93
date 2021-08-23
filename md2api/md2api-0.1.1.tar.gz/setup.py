# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['md2api']

package_data = \
{'': ['*']}

install_requires = \
['GitPython>=3.1.20,<4.0.0', 'markdown>=3.3.4,<4.0.0']

entry_points = \
{'console_scripts': ['md2api = mf2api:main']}

setup_kwargs = {
    'name': 'md2api',
    'version': '0.1.1',
    'description': '',
    'long_description': None,
    'author': 'sumeshi',
    'author_email': 'j15322sn@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
