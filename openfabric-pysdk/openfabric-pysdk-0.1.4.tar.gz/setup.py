# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['openfabric_pysdk']

package_data = \
{'': ['*'], 'openfabric_pysdk': ['templates/*']}

install_requires = \
['Flask-Cors>=3.0.10,<4.0.0',
 'Flask-RESTful>=0.3.9,<0.4.0',
 'Flask-SocketIO>=5.1.1,<6.0.0',
 'Flask>=2.0.1,<3.0.0',
 'eventlet>=0.31.1,<0.32.0',
 'flask-apispec>=0.11.0,<0.12.0',
 'gevent-websocket>=0.10.1,<0.11.0',
 'gevent>=21.8.0,<22.0.0']

setup_kwargs = {
    'name': 'openfabric-pysdk',
    'version': '0.1.4',
    'description': 'Openfabric Python SDK',
    'long_description': '',
    'author': 'Andrei Tara',
    'author_email': 'andrei@openfabric.ai',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://openfabric.ai',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
