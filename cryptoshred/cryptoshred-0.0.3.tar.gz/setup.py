# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['cryptoshred',
 'cryptoshred.app',
 'cryptoshred.app.business',
 'cryptoshred.app.ui']

package_data = \
{'': ['*']}

install_requires = \
['boto3>=1.17.105,<2.0.0',
 'cryptography>=3.4.7,<4.0.0',
 'pydantic>=1.8.2,<2.0.0',
 'python-dotenv>=0.19.0,<0.20.0',
 'rich>=10.4.0,<11.0.0',
 'typer>=0.3.2,<0.4.0']

extras_require = \
{'docs': ['sphinx-autodoc-typehints>=1.12.0,<2.0.0',
          'sphinx-rtd-theme>=0.5.2,<0.6.0',
          'sphinx-click>=3.0.1,<4.0.0',
          'Sphinx<4']}

entry_points = \
{'console_scripts': ['cryptoshred = cryptoshred.app.ui.cli:app']}

setup_kwargs = {
    'name': 'cryptoshred',
    'version': '0.0.3',
    'description': '',
    'long_description': '# Cryptoshred\n\nWelcome to cryptoshred. You can find more extensive documentation over at [readthedocs](https://cryptoshred.readthedocs.io/en/latest/).\n\nThis project arose manly out of the necessity to work with events that contain cryptoshredded information.\nIt is an implementation of cryptoshredding that is compatible with [this Java implementation](https://github.com/prisma-capacity/cryptoshred). It can either be used independently or together with [pyfactcast](https://pypi.org/project/pyfactcast/).\n\nContributions are welcome. Just get in touch.\n\n## Quickstart\n\nSimply `pip install cryptoshred` and get going. The cli is available as `cryptoshred` and\nyou can run `cryptoshred --help` to get up to speed on what you can do.\n\n## Development\n\nThis project uses `poetry` for dependency management and `pre-commit` for local checks.\n',
    'author': 'Eduard Thamm',
    'author_email': 'eduard.thamm@thammit.at',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gitlab.com/edthamm/cryptoshred',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
