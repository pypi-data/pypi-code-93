# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['grepy']

package_data = \
{'': ['*']}

entry_points = \
{'console_scripts': ['grepy = grepy:main']}

setup_kwargs = {
    'name': 'grepy',
    'version': '0.1.1',
    'description': 'A Grep clone',
    'long_description': '# Grepy\n\nA Python clone of [Grep](https://en.wikipedia.org/wiki/Grep).\n\n## Install\n\nYou can install [Chuy](https://pypi.org/project/chuy) from PyPI like any other package:\n\n```bash\npip install grepy\n```\n\nTo get the last version:\n\n```bash\npip install git+https:/github.com/UltiRequiem/grepy\n```\n\nIf you use Linux, you may need to install this with sudo to\nbe able to access the command throughout your system.\n\n### License\n\nGrepy is licensed under the [MIT License](./LICENSE).\n',
    'author': 'Eliaz Bobadilla',
    'author_email': 'eliaz.bobadilladev@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/UltiRequiem/grep',
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
