# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['delphai_utils']

package_data = \
{'': ['*']}

extras_require = \
{'config': ['omegaconf>=2.1.0,<3.0.0',
            'memoization>=0.3.1,<0.4.0',
            'python-dotenv>=0.14.0,<0.15.0',
            'kubernetes>=12.0.0,<13.0.0',
            'coloredlogs>=14.0,<15.0',
            'deepmerge>=0.1.0,<0.2.0',
            'keyring>=21.5.0,<22.0.0'],
 'database': ['motor>=2.3.0,<3.0.0'],
 'elasticsearch': ['elasticsearch[async]>=7.9.1,<8.0.0'],
 'grpc': ['grpcio>=1.32.0,<2.0.0',
          'starlette==0.12.9',
          'hypercorn>=0.10.2,<0.11.0',
          'validate_email>=1.3,<2.0',
          'ipaddress>=1.0.23,<2.0.0',
          'jinja2>=2.11.2,<3.0.0',
          'markupsafe>=1.1.1,<2.0.0',
          'starlette-prometheus>=0.7.0,<0.8.0',
          'grpcio-health-checking>=1.32.0,<2.0.0',
          'grpcio-reflection>=1.32.0,<2.0.0',
          'googleapis-common-protos>=1.52.0,<2.0.0',
          'httpx>=0.14.0,<0.15.0',
          'python-jose>=3.2.0,<4.0.0']}

setup_kwargs = {
    'name': 'delphai-utils',
    'version': '0.2.31',
    'description': 'delphai backend utilities',
    'long_description': None,
    'author': 'Barath Kumar',
    'author_email': 'barath@delphai.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/delphai/backend-utils',
    'packages': packages,
    'package_data': package_data,
    'extras_require': extras_require,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
