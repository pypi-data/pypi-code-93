# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['resilient_exporters',
 'resilient_exporters.exceptions',
 'resilient_exporters.exporters']

package_data = \
{'': ['*']}

install_requires = \
['orjson', 'requests']

extras_require = \
{'all': ['pymongo>=3,<4',
         'elasticsearch[async]>6.0',
         'psycopg2-binary>=2.7,<3.0'],
 'elastic': ['elasticsearch[async]>6.0'],
 'mongo': ['pymongo>=3,<4'],
 'postgres': ['psycopg2-binary>=2.7,<3.0']}

setup_kwargs = {
    'name': 'resilient-exporters',
    'version': '0.1.6',
    'description': 'A package to export data to databases resiliently.',
    'long_description': '# Resilient Exporters\n![PyPI](https://img.shields.io/pypi/v/resilient-exporters?logo=pypi&logoColor=white&style=for-the-badge)\n![GitHub Build Status](https://img.shields.io/github/workflow/status/arbfay/resilient-exporters/Python%20package?logo=github&style=for-the-badge)\n![License](https://img.shields.io/github/license/arbfay/resilient-exporters?style=for-the-badge)\n![Python Version](https://img.shields.io/badge/3.6+%20-%2314354C.svg?label=PYTHON&style=for-the-badge&logo=python&logoColor=white)\n\nResilient-exporters abstracts away common tasks when sending or saving data from an application. It has been designed to send data to different targets and manage common issues for applications running on edge devices such as a Raspberry Pi or Nvidia Jetson Nano:\n- Internet connection interruptions;\n- Highly variable frequency of data transfers;\n\nIf a connection is lost, it automatically saves the data and retries later when the connection is recovered and when a new request to send data is made. To avoid consuming too much memory or disk space, it has a specific configurable flush.\n\nIf an application wants to send more data than is momentally manageable, it multiplies the transmission jobs (using multithreading, if available) and saves the data (queuing), to avoid back-pressure and reducing the application\'s speed.\n\nOf course, it can break if:\n- the data to transmit is _almost always_ more important than the available bandwidth;\n- the interruptions are too long compared to the available memory or disk space;\n\nWe have designed it particularly for a Raspberry Pi 3B+ device running a Linux distribution.\n\n## Installation\nTo use the package:\n```\npip install resilient-exporters\n```\n\nWith all the additional packages needed for the different exporters:\n```\npip install resilient-exporters[all]\n```\n\n### Dev installation\nIf you\'d like to have a editable, up-to-date version of the files, do:\n```\ngit clone https://github.com/arbfay/resilient-exporters.git && \\\npip install -e resilient-exporters/ && \\\npip install -r resilient-exporters/dev_requirements.txt\n```\n\n## Usage\nCurrently supported:\n- Text file\n- MongoDB\n- ElasticSearch\n- PostgreSQL\n\nSome features for some exporters might be missing. Raise an issue on Github to ask for an implementation and help improve the package.\n\n### Store in a file\n```python\nfrom resilient_exporters import FileExporter\n\nexporter = FileExporter(target_file="mydata.txt",\n                        max_lines=100)\n\nmydata = "line of text"\nexporter.send(mydata)\n```\n\n### To MongoDB\n```python\nfrom resilient_exporters import MongoDBExporter\n\nexporter = MongoDBExporter(target_ip="127.0.0.1",\n                           target_port=27017,\n                           username="username",\n                           password="password",\n                           default_db="my_db",\n                           default_collection="my_collection")\n\nmydata = {"field1": "value1"}\nexporter.send(mydata)\n```\n\n### To ElasticSearch\n```python\nfrom resilient_exporters import ElasticSearchExporter\n\nexporter = ElasticSearchExporter(target_ip="127.0.0.1",\n                                 default_index="my_index",\n                                 use_ssl=True,\n                                 ssl_certfile="/path/to/file",\n                                 sniff_on_start=True)\n\nmydata = {"field1": "value1"}\nexporter.send(mydata)\n```\n\n### To PostgreSQL\n```python\nfrom resilient_exporters.exporters import PostgreSQLExporter\n\nexporter = PostgreSQLExporter(target_host="myserver.domain.net",\n                              username="username",\n                              password="my-password",\n                              database="profiles",\n                              default_table="scientists")\n\ndata = {"name": "Richard Feynman",\n        "age": 69}\nexporter.send(data)\n```\n\n### Multiple distant targets - Pools\nEdge devices are more and more powerful, and are capable of managing multiple distant targets without much overhead thanks to `resilient-exporters`. If you\'re taking advantage of this, you might need sometimes to replicate data across different databases of the same type (e.g. NoSQL, document-based databases). However, if you use multiple exporters, all the features will be duplicated and can generate inefficiencies (multiple temporary files, multiple queues, etc.).\n\nInstead, use `resilient_exporters.ExporterPool` which pools exporters _and_ other pools to expose only one `send` method for all the exporters and to ensure a more efficient management of the resources. To use it:\n```python\nfrom resilient_exporters import ExporterPool\nfrom resilient_exporters import MongoDBExporter, ElasticSearchExporter\n\nexporters = [\n  MongoDBExporter(target_ip="127.0.1.10",\n                  target_port=1234,\n                  default_db="my_db",\n                  default_collection="my_collection"),\n  ElasticSearchExporter(cloud_id="cloud id",\n                        api_key="api key",\n                        default_index="my_index")]\n\npool = ExporterPool(exporters, use_memory=False)\n\nmydata = {"metric": 2}\npool.send(mydata)\n```\n\n## Transform data before sending\nTo transform data before it gets sent by an exporter or a pool, one can add a function that takes the input data and returns the transformed data:\n```python\nfrom resilient_exporters import MongoDBExporter\n\ndef transform(data):\n  data["metric"] = (data["metric"] / 2) * .5\n  return data\n\nexporter = MongoDBExporter(target_ip="127.0.1.10",\n                           target_port=1234,\n                           default_db="my_db",\n                           default_collection="my_collection",\n                           transform=transform)\n\nmydata = {"metric": 2}\nexporter.send(mydata)\n```\n>**NOTE**: it can also be passed to a pool with the same key argument `tranform` at initialisation. When doing so, transform functions of individual exporters will be superseded by the pool\'s transform function.\n\n## Additional information\nThe `resilient_exporters.Exporter` is at the core of the package. All the other exporters inherits from it.\n\n`Exporter` manages the export of data to a target, however each target need specific logic to send data. All these subclasses, such as `FileExporter` or `MongoDBExporter`, implements the `Exporter.send` method and manages the needed options. Some exporters might need additional packages to be usable:\n- `pymongo` for `MongoDBExporter`\n- `elasticsearch` for `ElasticSearchExporter`\n- `psycopg2` for `PostgreSQLExporter`\n\n## Documentation\nMore documentation available [here.](https://resilient-exporters.readthedocs.io)\n\n## Suggestions and contribution\nPlease open a GitHub issue for bugs or feature requests.\nContact the contributors for participating.\n',
    'author': 'Fayçal Arbai',
    'author_email': 'arbai.faycal@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/arbfay/resilient-exporters.git',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.6',
}


setup(**setup_kwargs)
