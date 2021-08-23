# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fs', 'fs.onedrivefs']

package_data = \
{'': ['*']}

install_requires = \
['fs>=2.0.6', 'requests-oauthlib>=1.2.0', 'requests>=2.20']

entry_points = \
{'fs.opener': ['onedrive = fs.onedrivefs.opener:OneDriveFSOpener']}

setup_kwargs = {
    'name': 'fs.onedrivefs',
    'version': '1.0.0',
    'description': 'Pyfilesystem2 implementation for OneDrive using Microsoft Graph API',
    'long_description': '# fs.onedrivefs\n\nImplementation of pyfilesystem2 file system using OneDrive\n\n![image](https://github.com/rkhwaja/fs.onedrivefs/workflows/ci/badge.svg) [![codecov](https://codecov.io/gh/rkhwaja/fs.onedrivefs/branch/master/graph/badge.svg)](https://codecov.io/gh/rkhwaja/fs.onedrivefs) [![PyPI version](https://badge.fury.io/py/fs.onedrivefs.svg)](https://badge.fury.io/py/fs.onedrivefs)\n\n# Usage\n\n``` python\nonedriveFS = OneDriveFS(\n  clientId=<your client id>,\n  clientSecret=<your client secret>,\n  token=<token JSON saved by oauth2lib>,\n  SaveToken=<function which saves a new token string after refresh>)\n\n# onedriveFS is now a standard pyfilesystem2 file system\n```\n\nRegister your app [here](https://docs.microsoft.com/en-us/graph/auth-register-app-v2) to get a client ID and secret\n',
    'author': 'Rehan Khwaja',
    'author_email': 'rehan@khwaja.name',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/rkhwaja/fs.onedrivefs',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6',
}


setup(**setup_kwargs)
