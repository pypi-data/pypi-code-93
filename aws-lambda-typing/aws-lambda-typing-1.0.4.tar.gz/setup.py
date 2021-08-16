# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['aws_lambda_typing',
 'aws_lambda_typing.context',
 'aws_lambda_typing.events',
 'aws_lambda_typing.responses']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'aws-lambda-typing',
    'version': '1.0.4',
    'description': 'A package that provides type hints for AWS Lambda event, context and response objects',
    'long_description': "# AWS Lambda Typing\n\n![build](https://github.com/MousaZeidBaker/aws-lambda-typing/workflows/Publish/badge.svg)\n![test](https://github.com/MousaZeidBaker/aws-lambda-typing/workflows/Test/badge.svg)\n[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)\n[![pypi_v](https://img.shields.io/pypi/v/aws-lambda-typing.svg)](https://pypi.org/project/aws-lambda-typing)\n[![pypi_dm](https://img.shields.io/pypi/dm/aws-lambda-typing.svg)](https://pypi.org/project/aws-lambda-typing)\n\nA package that provides type hints for AWS Lambda event, context and response\nobjects. It's a convenient way to get autocomplete and type hints built into\nIDEs. Type annotations are not checked at runtime but are only enforced by\nthird party tools such as type checkers, IDEs, linters, etc.\n\n## Usage\nAWS SQS message event example\n\n```python\nimport aws_lambda_typing as lambda_typing\n\n\ndef handler(event: lambda_typing.SQSEvent, context: lambda_typing.Context) -> None:\n\n    for record in event['Records']:\n        print(context.get_remaining_time_in_millis())\n\n        print(record['body'])\n```\n\n## Demo\n### IDE autocomplete\n![ide_autocomplete](https://raw.githubusercontent.com/MousaZeidBaker/aws-lambda-typing/master/media/ide_autocomplete.gif)\n\n### IDE code reference information\n![code_reference_information](https://raw.githubusercontent.com/MousaZeidBaker/aws-lambda-typing/master/media/code_reference_information.gif)\n\n## Test\nInstall project dependencies\n```shell\npoetry install\n```\n\nActivate virtualenv\n```shell\npoetry shell\n```\n\nRun tests\n```shell\nmypy tests\n```\n\n## License\n### The MIT License\n[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)\n",
    'author': 'Mousa Zeid Baker',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/MousaZeidBaker/aws-lambda-typing',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
