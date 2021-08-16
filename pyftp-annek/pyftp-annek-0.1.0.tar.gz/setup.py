# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['pyftp_annek']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.0.1,<9.0.0']

entry_points = \
{'console_scripts': ['pyftp = pyftp_annek.cli:main']}

setup_kwargs = {
    'name': 'pyftp-annek',
    'version': '0.1.0',
    'description': 'FTP Uploader',
    'long_description': None,
    'author': 'Michael MacKenna',
    'author_email': 'mpmackenna@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
