# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['aiobotocore']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.3.1,<4.0.0',
 'aioitertools>=0.5.1,<0.6.0',
 'botocore>=1.20.0,<2.0.0',
 'wrapt>=1.10.10,<2.0.0']

extras_require = \
{'awscli': ['awscli>=1.18.0,<2.0.0'], 'boto3': ['boto3>=1.17.0,<2.0.0']}

setup_kwargs = {
    'name': 'aio-botocore',
    'version': '1.3.3',
    'description': 'Async client for aws services using botocore and aiohttp',
    'long_description': 'aio-botocore\n============\n\nThe sole purpose of this fork is to release a version of\n[aiobotocore](https://github.com/aio-libs/aiobotocore) with\nrelaxed constraints on the dependencies for botocore and boto3.\nThis should enable algorithms for resolving dependencies to\nwork more efficiently with this library.\n\nHopefully any risks in relaxing the versions allowed for\nbotocore and boto3 are minimal.  However, use at your own\nrisk (i.e. use your own unit tests and test coverage to\nmanage your risks).\n\nIf the original library works for your purposes, use it\ninstead of this library.  If changes to this library are working,\nsome form of the changes might get integrated into the original\nproject.  If so, hopefully this library will cease to exist\n(or at least cease to be maintained in this form).\n\nInstall\n-------\n::\n\n    $ pip install aio-botocore\n\nThe original library is installed using\n\n    $ pip install aiobotocore\n',
    'author': 'Nikolay Novik',
    'author_email': 'nickolainovik@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'http://aiobotocore.readthedocs.io',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
