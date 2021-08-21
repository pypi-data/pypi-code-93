# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['kgdata',
 'kgdata.dbpedia',
 'kgdata.misc',
 'kgdata.wikidata',
 'kgdata.wikidata.models',
 'kgdata.wikipedia']

package_data = \
{'': ['*']}

install_requires = \
['beautifulsoup4>=4.9.3,<5.0.0',
 'chardet>=4.0.0,<5.0.0',
 'cityhash>=0.2.3,<0.3.0',
 'fastnumbers>=3.1.0,<4.0.0',
 'loguru>=0.5.3,<0.6.0',
 'networkx>=2.5.1,<3.0.0',
 'numpy>=1.20.3,<2.0.0',
 'orjson>=3.5.2,<4.0.0',
 'pyspark==3.0.3',
 'rdflib>=5.0.0,<6.0.0',
 'redis>=3.5.3,<4.0.0',
 'requests>=2.25.1,<3.0.0',
 'rocksdb>=0.7.0,<0.8.0',
 'ruamel.yaml>=0.17.4,<0.18.0',
 'six>=1.16.0,<2.0.0',
 'tqdm>=4.60.0,<5.0.0',
 'ujson>=4.0.2,<5.0.0']

setup_kwargs = {
    'name': 'kgdata',
    'version': '1.2.1',
    'description': 'Library to process dumps of knowledge graphs (Wikipedia, DBpedia, Wikidata)',
    'long_description': None,
    'author': 'Binh Vu',
    'author_email': 'binh@toan2.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
