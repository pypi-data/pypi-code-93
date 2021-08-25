# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ahadith']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.26.0,<3.0.0']

setup_kwargs = {
    'name': 'ahadith',
    'version': '0.1.0',
    'description': 'A module which helps you to retrieve (sahih) ahadith',
    'long_description': '# ahadith\n\n## Motivation\n\nA little python library to consume [hadith.json](https://github.com/4thel00z/hadith.json).\n## License\n\nThis project is licensed under the GPL-3 license.\n',
    'author': '4thel00z',
    'author_email': '4thel00z@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/4thel00z/ahadith',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6.2,<4.0',
}


setup(**setup_kwargs)
