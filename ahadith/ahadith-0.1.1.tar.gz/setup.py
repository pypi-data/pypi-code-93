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
    'version': '0.1.1',
    'description': 'A module which helps you to retrieve (sahih) ahadith',
    'long_description': '# ahadith\n\n![hadith.json.png](https://raw.githubusercontent.com/4thel00z/logos/master/hadith.json.png)\n\n## Motivation\n\nA little python library to consume [hadith.json](https://github.com/4thel00z/hadith.json).\n\n## Installation\n\n```\npip install ahadith\n```\n\n## Usage\n### Get bukhari book by id\n\n```python\nfrom ahadith import bukhari\n\nbook = bukhari(1)\nfirst_hadith = book[0]\nprint(first_hadith)\n```\n\n## License\n\nThis project is licensed under the GPL-3 license.\n',
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
