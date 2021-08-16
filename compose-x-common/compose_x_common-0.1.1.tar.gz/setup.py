# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['compose_x_common', 'compose_x_common.aws']

package_data = \
{'': ['*']}

extras_require = \
{'aws': ['boto3>=1.18.0,<2.0.0']}

setup_kwargs = {
    'name': 'compose-x-common',
    'version': '0.1.1',
    'description': 'Common Library for Compose-X Projects',
    'long_description': '=====================\nCompose-X -- Common\n=====================\n\n\n.. image:: https://img.shields.io/pypi/v/compose_x_common.svg\n        :target: https://pypi.python.org/pypi/compose_x_common\n\n.. image:: https://readthedocs.org/projects/compose-x-commons-lib/badge/?version=latest\n        :target: https://compose-x-commons-lib.readthedocs.io/en/latest/?version=latest\n        :alt: Documentation Status\n\n\n\n\nStandalone library of reusable functions"\n\n\n* Free software: MPL-2.0\n* Documentation: https://compose-x-common.readthedocs.io.\n',
    'author': 'John Preston',
    'author_email': 'john@compose-x.io',
    'maintainer': 'John Preston',
    'maintainer_email': 'john@compose-x.io',
    'url': 'https://github.com/compose-x/compose-x-common-libs/',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
