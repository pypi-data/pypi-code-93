# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dj003']

package_data = \
{'': ['*']}

install_requires = \
['Django>=3.2.6,<4.0.0']

extras_require = \
{'pyopenxl': ['selenium>=3,<4']}

entry_points = \
{'console_scripts': ['one-script = DJ003.run:main']}

setup_kwargs = {
    'name': 'dj003',
    'version': '0.1.0',
    'description': 'This is a django project',
    'long_description': None,
    'author': 'xiaodeng',
    'author_email': 'xiaodengteacher@qq.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
