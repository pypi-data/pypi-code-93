# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['aws_custom_ews_kafka_resources']

package_data = \
{'': ['*']}

install_requires = \
['tbump==6.3.1', 'troposphere>=3.0,<4.0']

setup_kwargs = {
    'name': 'aws-custom-ews-kafka-resources',
    'version': '0.2.0',
    'description': 'Custom Resources for AWS CloudFormation representing Kafka assets management',
    'long_description': '=================================\nKafka Topic class for Troposphere\n=================================\n\nLib to represent kafka topic that can then be used with Troposphere\n\nHow to use\n==========\n\nInstall\n-------\n\n.. code-block:: bash\n\n    pip install aws_custom_ews_kafka_topic\n\nDeploy via Custom resource (self-managed Lambda)\n-------------------------------------------------\n\n.. code-block:: yaml\n\n    from aws_custom_ews_kafka_topic.custom import KafkaTopic\n\n    topic = KafkaTopic(\n      ServiceToken=Ref(FunctionArn),\n      Name="new-kafka-topic",\n      PartitionsCount=6\n    )\n\nDeploy via Private Registry resource type\n------------------------------------------\n\n.. code-block:: yaml\n\n    from aws_custom_ews_kafka_topic.resource import KafkaTopic\n\n    topic = KafkaTopic(\n      Name="new-kafka-topic",\n      PartitionsCount=6\n    )\n\nExample from CLI\n------------------\n\n.. code-block:: bash\n\n    >>> from troposphere import Template\n    >>> from aws_custom_ews_kafka_topic.resource import KafkaTopic\n    >>> t = KafkaTopic("newtopic", Name="toto", PartitionsCount=6, BootstrapServers="toto.net")\n    >>> c = Template()\n    >>> c.add_resource(t)\n    >>> print(c.to_yaml())\n    Resources:\n      newtopic:\n        Properties:\n          BootstrapServers: toto.net\n          Name: toto\n          PartitionsCount: 6\n        Type: EWS::Kafka::Topic\n\n\nCredits\n=======\n\nThis package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.\n\n.. _Cookiecutter: https://github.com/audreyr/cookiecutter\n.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage\n',
    'author': 'John Preston',
    'author_email': 'john@ews-network.net',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
