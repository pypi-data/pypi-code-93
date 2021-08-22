# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['smartmeter', 'smartmeter._async']

package_data = \
{'': ['*']}

install_requires = \
['importlib-metadata>=4.6.4,<5.0.0',
 'lxml>=4.6.3,<5.0.0',
 'requests>=2.24.0,<3.0.0']

extras_require = \
{'async': ['aiohttp>=3.7.4,<4.0.0', 'async_timeout>=3.0.1,<4.0.0']}

setup_kwargs = {
    'name': 'vienna-smartmeter',
    'version': '0.2.0',
    'description': 'Python library to access the Wiener Netze Smart Meter private API.',
    'long_description': '<h1 align="center">\n  Vienna Smart Meter\n</h1>\n<h4 align="center">An unofficial python wrapper for the <a href="https://www.wienernetze.at/smartmeter" target="_blank">Wiener Netze Smart Meter</a> private API.\n</h4>\n\n[![PyPI Version](https://img.shields.io/pypi/v/vienna-smartmeter)](https://pypi.org/project/vienna-smartmeter/)\n[![Build](https://github.com/platysma/vienna-smartmeter/actions/workflows/build.yml/badge.svg)](https://github.com/platysma/vienna-smartmeter/actions/workflows/build.yml)\n[![Code Coverage](https://codecov.io/gh/platysma/vienna-smartmeter/branch/main/graph/badge.svg)](https://codecov.io/gh/platysma/vienna-smartmeter)\n[![Code Quality](https://api.codeclimate.com/v1/badges/3130fa0ba3b7993fbf0a/maintainability)](https://codeclimate.com/github/platysma/vienna-smartmeter)\n\n## Features\n\n- Access energy usage for specific meters\n- Get profile information\n- View, edit & delete events (Ereignisse)\n\n## Installation\n\nInstall with pip:\n\n`pip install vienna-smartmeter`\n\n## How To Use\n\nImport the Smartmeter client, provide login information and access available api functions:\n\n```python\nfrom smartmeter import Smartmeter\n\nusername = \'YOUR_LOGIN_USER_NAME\'\npassword = \'YOUR_PASSWORD\'\n\napi = Smartmeter(username, password)\nprint(api.profil())\n```\n\n## Contributing\n\nPull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.\n\nMake sure to add or update tests as appropriate.\n\n## License\n\n> You can check out the full license [here](https://github.com/platysma/vienna-smartmeter/blob/main/LICENSE)\n\nThis project is licensed under the terms of the **MIT** license.\n\n## Legal\n\nDisclaimer: This is not affliated, endorsed or certified by Wiener Netze. This is an independent and unofficial API. Strictly not for spam. Use at your own risk.\n',
    'author': 'Platysma',
    'author_email': 'platysma.dev@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/platysma/vienna-smartmeter',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.6.1,<4.0.0',
}


setup(**setup_kwargs)
