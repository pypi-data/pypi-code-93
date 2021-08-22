# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['aws_lambda_typing',
 'aws_lambda_typing.context',
 'aws_lambda_typing.events',
 'aws_lambda_typing.responses']

package_data = \
{'': ['*']}

install_requires = \
['typing-extensions>=3.10.0,<4.0.0']

setup_kwargs = {
    'name': 'aws-lambda-typing',
    'version': '2.0.0',
    'description': 'A package that provides type hints for AWS Lambda event, context and response objects',
    'long_description': "# AWS Lambda Typing\n\n![build](https://github.com/MousaZeidBaker/aws-lambda-typing/workflows/Publish/badge.svg)\n![test](https://github.com/MousaZeidBaker/aws-lambda-typing/workflows/Test/badge.svg)\n![LICENSE](https://img.shields.io/badge/License-MIT-yellow.svg)\n![python_version](https://img.shields.io/badge/python-%3E=3.6-blue.svg)\n![pypi_v](https://img.shields.io/pypi/v/aws-lambda-typing.svg)\n![pypi_dm](https://img.shields.io/pypi/dm/aws-lambda-typing.svg)\n\nA package that provides type hints for AWS Lambda event, context and response\nobjects. It's a convenient way to get autocomplete and type hints built into\nIDEs. Type annotations are not checked at runtime but are only enforced by\nthird party tools such as type checkers, IDEs, linters, etc.\n\n##### Table of Contents\n- [Usage](#usage)\n- [Demo](#demo)\n- [Types](#types)\n  - [Context](#context)\n  - [Events](#events)\n  - [Responses](#responses)\n- [Test](#test)\n- [License](#license)\n\n## Usage\n### Example: AWS SQS event\n\n```python\nfrom aws_lambda_typing import context as context_, events\n\n\ndef handler(event: events.SQSEvent, context: context_.Context) -> None:\n    for record in event['Records']:\n        print(record['body'])\n\n    print(context.get_remaining_time_in_millis())\n\n    message: events.sqs.SQSMessage\n\n```\n\n## Demo\n### IDE autocomplete\n![ide_autocomplete](https://raw.githubusercontent.com/MousaZeidBaker/aws-lambda-typing/master/media/ide_autocomplete.gif)\n\n### IDE code reference information\n![code_reference_information](https://raw.githubusercontent.com/MousaZeidBaker/aws-lambda-typing/master/media/code_reference_information.gif)\n\n## Types\n### Context\n- Context\n\n### Events\n- APIGatewayProxyEventV1\n- APIGatewayProxyEventV2\n- CloudWatchEventsMessageEvent\n- CloudWatchLogsEvent\n- CodePipelineEvent\n- ConfigEvent\n- DynamoDBStreamEvent\n- KinesisFirehoseEvent\n- KinesisStreamEvent\n- MQEvent\n- S3Event\n- S3BatchEvent\n- SESEvent\n- SNSEvent\n- SQSEvent\n\n### Responses\n- APIGatewayProxyResponseV1\n- APIGatewayProxyResponseV2\n- S3BatchResponse\n\n## Test\nActivate virtualenv & Install project dependencies\n```shell\npoetry shell && poetry install\n```\n\nRun tests\n```shell\nmypy tests\n```\n\n## License\n### The MIT License\n![LICENSE](https://img.shields.io/badge/License-MIT-yellow.svg)\n",
    'author': 'Mousa Zeid Baker',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/MousaZeidBaker/aws-lambda-typing',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
