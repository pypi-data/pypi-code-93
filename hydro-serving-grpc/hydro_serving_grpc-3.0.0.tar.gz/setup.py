# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['hydro_serving_grpc',
 'hydro_serving_grpc.interpretability',
 'hydro_serving_grpc.interpretability.visualization',
 'hydro_serving_grpc.monitoring',
 'hydro_serving_grpc.monitoring.auto_od',
 'hydro_serving_grpc.monitoring.sonar',
 'hydro_serving_grpc.serving',
 'hydro_serving_grpc.serving.contract',
 'hydro_serving_grpc.serving.discovery',
 'hydro_serving_grpc.serving.gateway',
 'hydro_serving_grpc.serving.manager',
 'hydro_serving_grpc.serving.runtime']

package_data = \
{'': ['*']}

install_requires = \
['grpcio>=1.38.0,<2.0.0', 'protobuf>=3.17.2,<4.0.0']

setup_kwargs = {
    'name': 'hydro-serving-grpc',
    'version': '3.0.0',
    'description': 'Protobuf messages and GRPC API for Hydrosphere Serving platform',
    'long_description': '# Hydrosphere Serving proto/grpc library\n\nContains compiled messages and service interfaces.',
    'author': 'Hydrospheredata',
    'author_email': 'info@hydrosphere.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Hydrospheredata/hydro-serving-protos',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
