# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['kusanagi', 'kusanagi.sdk', 'kusanagi.sdk.lib', 'kusanagi.sdk.lib.payload']

package_data = \
{'': ['*']}

install_requires = \
['msgpack==1.0.0', 'pyzmq==19.0.0']

setup_kwargs = {
    'name': 'kusanagi-sdk-python',
    'version': '3.0.1',
    'description': 'Python SDK for the KUSANAGI™ framework',
    'long_description': None,
    'author': 'Jeronimo Albi',
    'author_email': 'jeronimo.albi@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'http://kusanagi.io/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
