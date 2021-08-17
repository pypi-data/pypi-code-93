# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['quoteran']

package_data = \
{'': ['*']}

install_requires = \
['colorama>=0.4.4,<0.5.0', 'requests>=2.26.0,<3.0.0']

entry_points = \
{'console_scripts': ['quoteran = quoteran:main']}

setup_kwargs = {
    'name': 'quoteran',
    'version': '1.1.0',
    'description': 'Random quotes on Terminal',
    'long_description': '# quoteran\n\nGet random quotes in terminal.\n\nThis project fetch the [Quotable.io API](https://api.quotable.io/random).\n\n![Screenshot](./assets/screenshot.png)\n\n## Install\n\nYou can install [Quoteran](https://pypi.org/project/quteran) from PyPI:\n\n```bash\npip install quoteran\n```\n\nTo get the last version:\n\n```bash\npip install git+https:/github.com/UltiRequiem/quoteran\n```\n\nIf you use Linux, you may need to install this with sudo to\nbe able to access the command throughout your system.\n\n## Usage\n\n```bash\nquoteran\n```\n\n### License\n\nThis project is Licensed under the [MIT](./LICENSE) License.\n\n### Alternative\n\nI also developed this in Nodejs: [UltiRequiem/ranmess](https://github.com/UltiRequiem/ranmess)\n\n![Benchmark Screenshot](./assets/benchmark.png)\n\nThe version written in Nodejs is significantly faster,\nand it was even easier to develop and publish than this.\n',
    'author': 'Eliaz Bobadilla',
    'author_email': 'eliaz.bobadilladev@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/UltiRequiem/quoteran',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
