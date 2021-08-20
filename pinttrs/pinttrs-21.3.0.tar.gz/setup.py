# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['pinttr']

package_data = \
{'': ['*']}

install_requires = \
['attrs', 'pint>=0.16']

setup_kwargs = {
    'name': 'pinttrs',
    'version': '21.3.0',
    'description': 'Pint meets attrs',
    'long_description': "# Pinttrs\n\n*Pint meets attrs*\n\n[![PyPI version](https://img.shields.io/pypi/v/pinttrs?color=blue&style=flat-square)](https://pypi.org/project/pinttrs)\n[![Conda version](https://img.shields.io/conda/v/eradiate/pinttrs?color=blue&style=flat-square)](https://anaconda.org/eradiate/pinttrs)\n\n[![GitHub Workflow Status (branch)](https://img.shields.io/github/workflow/status/leroyvn/pinttrs/Tests/main?style=flat-square)](https://github.com/leroyvn/pinttrs/actions/workflows/tests.yml)\n[![Codecov](https://img.shields.io/codecov/c/gh/leroyvn/pinttrs?style=flat-square)](https://codecov.io/gh/leroyvn/pinttrs)\n[![Documentation Status](https://img.shields.io/readthedocs/pinttrs?style=flat-square)](https://pinttrs.readthedocs.io)\n\n[![Code style: black](https://img.shields.io/badge/code%20style-black-black?style=flat-square)](https://black.readthedocs.io)\n[![Imports: isort](https://img.shields.io/badge/%20imports-isort-blue?style=flat-square&labelColor=orange)](https://pycqa.github.io/isort)\n\n## Motivation\n\nThe amazing [`attrs`](https://www.attrs.org) library is a game-changer when it\ncomes to writing classes. Its initialisation sequence notably allows for\nautomated conversion and verification of attribute values. This package is an\nattempt at designing a system to apply units automatically and reliably to\nattributes with [Pint](https://pint.readthedocs.io).\n\n## Features\n\n- Attach automatically units to unitless values passed to initialise an attribute\n- Verify unit compatibility when assigning a value to an attribute\n- Interpret units in dictionaries with a simple syntax\n- Define unit context to vary unitless value interpretation dynamically\n\nCheck the [documentation](https://pinttrs.readthedocs.io) for more detail.\n\n## License\n\nPinttrs is distributed under the terms of the\n[MIT license](https://choosealicense.com/licenses/mit/).\n\n## About\n\nPinttrs is written and maintained by [Vincent Leroy](https://github.com/leroyvn).\n\nDevelopment is supported by [Rayference](https://www.rayference.eu).\n\nPinttrs is a component of the\n[Eradiate radiative transfer model](https://www.eradiate.eu).\n\nThe Pinttrs logo is based on\n[Agus Nugroho](https://www.iconfinder.com/nugrohoagus)'s glass icon and parts of\nthe ``attrs`` logo.\n",
    'author': 'Vincent Leroy',
    'author_email': 'vincent.leroy@rayference.eu',
    'maintainer': 'Vincent Leroy',
    'maintainer_email': 'vincent.leroy@rayference.eu',
    'url': 'https://github.com/leroyvn/pinttrs',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4',
}


setup(**setup_kwargs)
