# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['arg_services',
 'arg_services.base',
 'arg_services.base.v1',
 'arg_services.entailment',
 'arg_services.entailment.v1',
 'arg_services.graph',
 'arg_services.graph.v1',
 'arg_services.nlp',
 'arg_services.nlp.v1',
 'arg_services.retrieval',
 'arg_services.retrieval.v1',
 'arg_services_helper']

package_data = \
{'': ['*']}

install_requires = \
['grpcio-reflection>=1.39.0,<2.0.0',
 'grpcio>=1.32,<2.0',
 'protobuf>=3.15.8,<4.0.0']

extras_require = \
{'server': ['aiomultiprocess>=0.9.0,<0.10.0']}

setup_kwargs = {
    'name': 'arg-services',
    'version': '0.1.15',
    'description': 'GraphQL and gRPC schemas for Microservice-based Argumentation Machines.',
    'long_description': '# Argumentation Microservices\n',
    'author': 'Mirko Lenz',
    'author_email': 'info@mirko-lenz.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'http://recap.uni-trier.de',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
