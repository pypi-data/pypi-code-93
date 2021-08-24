# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['aws_cfn_kafka_admin_provider']

package_data = \
{'': ['*']}

install_requires = \
['aws-custom-ews-kafka-resources>=0.2.0,<0.3.0',
 'jsonschema>=3.2.0,<4.0.0',
 'pydantic>=1.8.2,<2.0.0',
 'troposphere>=3.0,<4.0']

entry_points = \
{'console_scripts': ['aws-cfn-kafka-admin-provider = '
                     'aws_cfn_kafka_admin_provider.cli:main']}

setup_kwargs = {
    'name': 'aws-cfn-kafka-admin-provider',
    'version': '0.6.0',
    'description': 'Converts simple YAML definitions of kafka ACLs and topics into AWS CFN templates',
    'long_description': '.. meta::\n    :description: Kafka admin via AWS CloudFormation\n    :keywords: AWS, CloudFormation, Kafka, Confluent\n\n====================\nKafka Admin Provider\n====================\n\nTool / Lib to transform a simply defined set of kafka topics and transforms the definition into an AWS CloudFormation\ntemplate that uses either EWS::Kafka::Topic or Custom::KafkaTopic (via AWS Lambda deployed in your account) to\ncreate/updated/delete your Kafka topics.\n\n\nInstallation\n==============\n\n.. code-block:: bash\n\n   python3 -m pip install aws_cfn_kafka_admin_provider\n\n\nUsage\n=======\n\nAs CLI\n-------\n\n.. code-block:: bash\n\n\n    aws-cfn-kafka-admin-provider --help\n    usage: aws-cfn-kafka-admin-provider [-h] -f FILE_PATH [-o OUTPUT_FILE] [--format {json,yaml}] [_ ...]\n\n    positional arguments:\n      _\n\n    optional arguments:\n      -h, --help            show this help message and exit\n      -f FILE_PATH, --file-path FILE_PATH\n                            Path to the kafka definition file\n      -o OUTPUT_FILE, --output-file OUTPUT_FILE\n                            Path to file output\n      --format {json,yaml}  Template format\n\n\nAs lib\n-------\n\n.. code-block:: python\n\n    from aws_cfn_kafka_admin_provider.aws_cfn_kafka_admin_provider import KafkaStack\n\n    stack = KafkaStack("/path/to/input/file.yaml")\n    stack.render_topics()\n\n\nRender models\n===============\n\n.. code-block:: bash\n\n    # Through makefile\n    make data-model\n\n    # Via CLI with\n\n    datamodel-codegen --input-file-type jsonschema \\\n        --input aws-cfn-kafka-admin-provider-schema.json \\\n        --output aws_cfn_kafka_admin_provider/model.py\n\nCredits\n========\n\nThis package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.\n\n.. _Cookiecutter: https://github.com/audreyr/cookiecutter\n.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage\n',
    'author': 'John Preston',
    'author_email': 'john@ews-network.net',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
