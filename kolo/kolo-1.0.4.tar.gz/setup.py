# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['kolo']

package_data = \
{'': ['*']}

install_requires = \
['appdirs>=1.4.4,<2.0.0']

setup_kwargs = {
    'name': 'kolo',
    'version': '1.0.4',
    'description': 'See everything happening in your running Django app',
    'long_description': '# Kolo\n\nSee everything happening in your running Django app\n\nMore information: https://kolo.app\n\nInstall instructions: https://github.com/kolofordjango/kolo\n\n![Annotated Kolo screenshot](https://user-images.githubusercontent.com/7718702/120298398-f3d17800-c2c1-11eb-9052-9adbbff0b5f5.png)\n',
    'author': 'Wilhelm Klopp',
    'author_email': 'team@kolo.app',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://kolo.app',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6.2,<4.0.0',
}


setup(**setup_kwargs)
