# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['servicetools']

package_data = \
{'': ['*']}

install_requires = \
['dramatiq[rabbitmq,watch]>=1.10',
 'pika>=1.2',
 'python-json-logger>=0.1',
 'starlette>=0.13',
 'structlog>=19']

setup_kwargs = {
    'name': 'python-service-tools',
    'version': '0.4.7',
    'description': 'Utilities for working with python services.',
    'long_description': '# python-service-tools\n\nUtilities for working with python services.\n\n![PyPI - Python Version](https://img.shields.io/pypi/pyversions/python-service-tools) ![PyPI](https://img.shields.io/pypi/v/python-service-tools.svg)\n\n## Usage\n\n### logging_config\n\nDefault configuration for structlog. \n\nConfigure json logging at the INFO level:\n```python\nfrom servicetools.logging_config import default_logging, LogFormat, Verbosity\n\ndefault_logging(Verbosity.INFO, LogFormat.JSON)\n```\n\nConfigure text logging at the DEBUG level:\n```python\nfrom servicetools.logging_config import default_logging, LogFormat, Verbosity\n\ndefault_logging(Verbosity.DEBUG, LogFormat.TEXT)\n```\n\nConfigure text logging at the DEBUG level and filter out external loggers:\n```python\nfrom servicetools.logging_config import default_logging, LogFormat, Verbosity\n\ndefault_logging(Verbosity.DEBUG, LogFormat.TEXT, ["extern_logger_1"])\n```\n\n### Log timing information for a function\n\nDecorator to add timing information to the logs:\n```python\nfrom servicetools.timer import timer\n\nimport structlog\n\n@timer(structlog.get_logger(__name__))\ndef some_function():\n    pass\n```\n\n### Create a namespace relative patch\n\nCreate namespace relative patches:\n```python\nimport some_package.sub_package.another_package as under_test\nfrom servicetools.testing import relative_patch_maker\n\npatch = relative_patch_maker(under_test.__name__)\n\nclass TestStuff:\n    #equivalent to @unittest.mock.patch("some_package.sub_package.another_package.something_to_patch")\n    @patch("something_to_patch")\n    def test_something(self, patched):\n        under_test.something()\n        patched.assert_called_once()\n\n    #equivalent to @unittest.mock.patch("some_package.sub_package.another_package.something_else_to_patch")\n    @patch("something_else_to_patch")\n    def test_something(self, patched):\n        under_test.something()\n        patched.assert_called_once()\n```\n\n### Starlette Structlog middleware \n\nMiddleware for [Starlette](https://www.starlette.io/) framework to log HTTP \nrequests to structlog. Log entries will be made at the start and end of\neach request. Error requests (400s and 500s) will also be logged. Any \ncalls that throw exceptions will be converted 500 responses.\n\n```python\nfrom servicetools.middleware import StructlogRequestMiddleware\nimport structlog\n\napp.add_middleware(StructlogRequestMiddleware(app, logger=structlog.get_logger(__name__)))\n```\n\nThere are options to customize the logging:\n\n```python\nimport logging\n\nimport structlog\nfrom servicetools.middleware import StructlogRequestMiddleware\n\napp.add_middleware(StructlogRequestMiddleware(\n    app,\n    logger=structlog.get_logger(__name__),\n    log_level=logging.DEBUG,  # Log at the DEBUG level.\n    ignored_status_codes={404},  # Do not log 404 errors.\n))\n```\n\n### Dramatiq Lazy Actor specification\nSpecification for [dramatiq](https://dramatiq.io/) actors that allows them to connect a broker\nexplicitly through the `init_actor` function rather than implicitly when they are created. This allows\nyou to defer setting up your Rabbitmq broker to a time of your choosing. To create a new actor that\nuses this behavior, set up your dramatiq actors like so\n```python\nimport dramatiq\n\nfrom servicetools.lazyactor import LazyActor\n\n@dramatiq.actor(actor_class=LazyActor)\ndef test_func(data: str) -> None:\n    print(data)\n```\n\nNow, whenever you have set up your Rabbitmq instance and connected to it, tell your actors to connect\nto it like so\n```python\nfrom dramatiq.brokers.rabbitmq import RabbitmqBroker\nfrom pika import PlainCredentials\nimport dramatiq\n\nbroker = RabbitmqBroker(\n    host="localhost",\n    credentials=PlainCredentials(username="user", password="password"),\n)\ndramatiq.set_broker(broker)\n\ntest_func.init_actor(broker=broker)\n```\n\n## Development Guide\n\nThis project uses [poetry](https://python-poetry.org/):\n\n```\n$ pip install poetry\n$ cd to/project/root\n$ poetry install\n```\n\n### Testing\n\nTesting is done via pytest.\n\n```\n$ poetry run pytest\n```',
    'author': 'Alexander Costas',
    'author_email': 'alexander.costas@mongodb.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/mongodb-labs/python-service-tools',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
