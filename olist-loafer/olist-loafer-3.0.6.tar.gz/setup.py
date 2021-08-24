# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['loafer', 'loafer.ext', 'loafer.ext.aws']

package_data = \
{'': ['*']}

install_requires = \
['aiobotocore[boto3]>=1.0.0,<2.0.0', 'cached-property>=1.3.0,<2.0.0']

setup_kwargs = {
    'name': 'olist-loafer',
    'version': '3.0.6',
    'description': 'Asynchronous message dispatcher for concurrent tasks processing',
    'long_description': "[![PyPI latest](https://img.shields.io/pypi/v/olist-loafer.svg?maxAge=2592000)](https://pypi.python.org/pypi/loafer)\n[![Python versions](https://img.shields.io/pypi/pyversions/olist-loafer.svg?maxAge=2592000)](https://pypi.python.org/pypi/loafer)\n[![License](https://img.shields.io/pypi/l/loafer.svg?maxAge=2592000)](https://pypi.python.org/pypi/olist-loafer)\n[![CircleCI](https://circleci.com/gh/olist/olist-loafer/tree/main.svg?style=svg)](https://circleci.com/gh/olist/olist-loafer/tree/main)\n[![Olist Sponsor](https://img.shields.io/badge/sponsor-olist-53b5f6.svg?style=flat-square)](http://opensource.olist.com/)\n\n\n**olist-loafer** is an asynchronous message dispatcher for concurrent tasks processing, with the following features:\n\n* Encourages decoupling from message providers and consumers\n* Easy to extend and customize\n* Easy error handling, including integration with sentry\n* Easy to create one or multiple services\n* Generic Handlers\n* Amazon SQS integration\n\n---\n:information_source: Currently, only AWS SQS is supported\n\n---\n\n## How to use\n\nA simple message forwader, from ``source-queue`` to ``destination-queue``:\n\n```python\nfrom loafer.ext.aws.handlers import SQSHandler\nfrom loafer.ext.aws.routes import SQSRoute\nfrom loafer.managers import LoaferManager\n\nroutes = [\n    SQSRoute('source-queue', handler=SQSHandler('destination-queue')),\n]\n\nif __name__ == '__main__':\n    manager = LoaferManager(routes)\n    manager.run()\n```\n\n## How to contribute\n\nFork this repository, make changes and send us a pull request. We will review your changes and apply them. Before sending us your pull request please check if you wrote and ran tests:\n\n```bash\nmake test\n```\n",
    'author': 'Olist',
    'author_email': 'developers@olist.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/olist/olist-loafer/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<3.10',
}


setup(**setup_kwargs)
