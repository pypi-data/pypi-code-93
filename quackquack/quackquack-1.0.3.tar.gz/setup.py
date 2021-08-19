# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': '.'}

packages = \
['qq',
 'qq.plugins',
 'qq.plugins.celery',
 'qq.plugins.jsonhack',
 'qq.plugins.jsonhack.tests',
 'qq.plugins.pyramid',
 'qq.plugins.pyramid.tests',
 'qq.plugins.sqlalchemy',
 'qq.plugins.sqlalchemy.tests',
 'qq.plugins.tests',
 'qq.plugins.tornado',
 'qq.tests']

package_data = \
{'': ['*']}

install_requires = \
['marshmallow_dataclass>=8.0.0,<9.0.0']

extras_require = \
{'alembic': ['alembic>=1.0.9,<2.0.0'],
 'celery': ['celery>=5.0.0,<6.0.0'],
 'developer': ['alembic>=1.0.9,<2.0.0',
               'sqlalchemy>=1.3.3,<2.0.0',
               'pyramid>=1.10.4,<2.0.0',
               'redis>=3.2.1,<4.0.0',
               'celery>=5.0.0,<6.0.0'],
 'pyramid': ['pyramid>=1.10.4,<2.0.0'],
 'redis': ['redis>=3.2.1,<4.0.0'],
 'sqlalchemy': ['sqlalchemy>=1.3.3,<2.0.0']}

setup_kwargs = {
    'name': 'quackquack',
    'version': '1.0.3',
    'description': 'Quack Quack: A simple application framework',
    'long_description': '# Quack Quack\n\nIf it quacks like a quack, then it\'s a Quack Quack.\nVersion: 1.0.2\n\n# Table of Contents\n1. [Overview](#overview)\n2. [Quick Using Guide](#quick-using-guide)\n3. [Installation](#installation)\n4. [Tutorial](docs/tutorial.md)\n    * [Configuration](docs/tutorial.md#configuration)\n    * [Starting](docs/tutorial.md#starting)\n    * [Using Context](docs/tutorial.md#using-context)\n    * [Using Injectors](docs/tutorial.md#using-injectors)\n    * [Creating Plugins](docs/tutorial.md#creating-plugins)\n5. [Plugins](docs/plugins.md)\n    * [Settings](docs/plugins.md#settings)\n    * [Logging](docs/plugins.md#logging)\n    * [Redis](docs/plugins.md#redis)\n    * [Pyramid Plugin](docs/pyramid.md)\n    * [Sqlalchemy Plugin](docs/sqlalchemy.md)\n    * [Json Plugin](docs/json.md)\n6. [Phases](docs/phases.md)\n    * [About Phases](docs/phases.md#about-phases)\n    * [Phase 0](docs/phases.md#phase-0)\n    * [Phase 1 - creating Configurator instance](docs/phases.md#phase-1---creating-configurator-instance)\n    * [Phase 2 - starting Configurator](docs/phases.md#phase-2---starting-configurator)\n    * [Extending Phases](#extending-phases)\n    * [Application Phase Start](docs/phases.md#application-phase-start)\n    * [Application Phase End](docs/phases.md#application-phase-end)\n7. More info\n    * [Changelog](docs/CHANGELOG.md)\n8. [Example](example/readme.md)\n\n\n# Overview\n\nThis project aims to resolve problem of configuring an application, which needs to\nhave initialization step (for example: for gathering settings or establishing\nconnections) and use Python style code (context managers and decorators) to get\nthose data.\n\nFor example, normally you would need to use two separate mechanism for settings\nin celery application and web application, because you should not use web\napplication startup process in the celery app. This package provide a solution\nfor this problem, by giving one simple and independent of other frameworks\nmechanism to implement everywhere.\n\n# Quick Using Guide\n\nTo use Quack Quack you need to create the application class (inherited from\n`qq.Application`) in which you need to add plugins. After configuring, you need to "start"\nthe application. After that you can use the configurator as context manager.\n\n```python\nfrom qq import Application, Context\nfrom qq.plugins import SettingsPlugin\n\nclass MyApplication(Application):\n    def create_plugins(self):\n        self.plugins["settings"] = SettingsPlugin(\'esett\')\n\napplication = MyApplication()\napplication.start(\'application\')\n\nwith Context(application) as ctx:\n    print(ctx["settings"])\n\n```\n\n`context.settings` in above example is variable made by the SettingsPlugin.\nIf you would like to know more, please go to the [Tutorial](docs/tutorial.md)\n\n# Installation\n\n```bash\npip install quackquack\n```\n',
    'author': 'Dominik Dlugajczyk',
    'author_email': 'msocek@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/socek/quackquack',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
