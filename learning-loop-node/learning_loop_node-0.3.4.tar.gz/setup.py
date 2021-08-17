# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['learning_loop_node',
 'learning_loop_node.converter',
 'learning_loop_node.detector',
 'learning_loop_node.tests',
 'learning_loop_node.trainer',
 'learning_loop_node.trainer.tests']

package_data = \
{'': ['*'], 'learning_loop_node.trainer.tests': ['test_data/*']}

install_requires = \
['aiofiles>=0.7.0,<0.8.0',
 'async_generator>=1.10,<2.0',
 'fastapi-socketio>=0.0.6,<0.0.7',
 'fastapi-utils>=0.2.1,<0.3.0',
 'fastapi>=0.63.0,<0.64.0',
 'icecream>=2.1.0,<3.0.0',
 'psutil>=5.8.0,<6.0.0',
 'pytest-watch>=4.2.0,<5.0.0',
 'python-multipart>=0.0.5,<0.0.6',
 'python-socketio[asyncio_client]>=5.0.4,<6.0.0',
 'requests>=2.25.1,<3.0.0',
 'simplejson>=3.17.2,<4.0.0',
 'uvicorn>=0.13.3,<0.14.0',
 'werkzeug>=2.0.1,<3.0.0']

setup_kwargs = {
    'name': 'learning-loop-node',
    'version': '0.3.4',
    'description': 'Python Library for Nodes which connect to the Zauberzeug Learning Loop',
    'long_description': '# Learning Loop Node\n\nThis Python library helps you to write your own Detection Nodes, Training Nodes and Converter Nodes for the Zauberzeug Learning Loop.\n\n## General Usage\n\nYou can configure connection to the learning loop by specifying the following environment variables before starting:\n\n- HOST=learning-loop.ai\n- ORGANIZATION=<your organization>\n- PROJECT=<your project>\n- USERNAME=<your username>\n- PASSWORD=<your password>\n\n## Detector Node\n\n## Trainer Node\n  \n- if the command line tool "jpeginfo" is installed, the downloader will drop corrupted images automatically\n\n## Converter Node\n\nA Conveter Node converts models from one format into another.\n\n### How to test the operability?\n\nAssumend there is a Converter Node which converts models of format \'format_a\' into \'format_b\'.\nUpload a model with\n`curl --request POST -F \'files=@my_model.zip\' https://learning-loop.ai/api/zauberzeug/projects/demo/format_a`\nThe model should now be available for the format \'format_a\'\n`curl "https://learning-loop.ai/api/zauberzeug/projects/demo/models?format=format_a"`\n\n```\n{\n  "models": [\n    {\n      "id": "3c20d807-f71c-40dc-a996-8a8968aa5431",\n      "version": "4.0",\n      "formats": [\n        "format_a"\n      ],\n      "created": "2021-06-01T06:28:21.289092",\n      "comment": "uploaded at 2021-06-01 06:28:21.288442",\n      ...\n    }\n  ]\n}\n\n```\n\nbut not in the format_b\n`curl "https://learning-loop.ai/api/zauberzeug/projects/demo/models?format=format_b"`\n\n```\n{\n  "models": []\n}\n```\n\nConnect the Node to the learning loop by simply starting the container.\nAfter a short time the converted Model should be available as well.\n`curl https://learning-loop.ai/api/zauberzeug/projects/demo/models?format=format_b`\n\n```\n{\n  "models": [\n    {\n      "id": "3c20d807-f71c-40dc-a996-8a8968aa5431",\n      "version": "4.0",\n      "formats": [\n        "format_a",\n        "format_b",\n      ],\n      "created": "2021-06-01T06:28:21.289092",\n      "comment": "uploaded at 2021-06-01 06:28:21.288442",\n      ...\n    }\n  ]\n}\n```\n',
    'author': 'Zauberzeug GmbH',
    'author_email': 'info@zauberzeug.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/zauberzeug/learning_loop_node',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
