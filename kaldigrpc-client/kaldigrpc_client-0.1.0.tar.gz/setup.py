# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['kaldigrpc_client', 'kaldigrpc_client.generated']

package_data = \
{'': ['*']}

install_requires = \
['grpcio-tools>=1.39.0,<2.0.0',
 'grpcio>=1.39.0,<2.0.0',
 'pydub>=0.25.1,<0.26.0']

entry_points = \
{'console_scripts': ['kaldigrpc-transcribe = '
                     'kaldigrpc_client.client:transcribe_wav']}

setup_kwargs = {
    'name': 'kaldigrpc-client',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Giorgos Paraskevopoulos',
    'author_email': 'geopar@central.ntua.gr',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
