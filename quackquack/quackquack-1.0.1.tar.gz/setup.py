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
    'version': '1.0.1',
    'description': 'Quack Quack: A simple application framework',
    'long_description': None,
    'author': 'Dominik Dlugajczyk',
    'author_email': 'msocek@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
