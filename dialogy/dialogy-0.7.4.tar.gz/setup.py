# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dialogy',
 'dialogy.base',
 'dialogy.cli',
 'dialogy.constants',
 'dialogy.plugins',
 'dialogy.plugins.postprocess',
 'dialogy.plugins.postprocess.text',
 'dialogy.plugins.postprocess.text.slot_filler',
 'dialogy.plugins.postprocess.text.voting',
 'dialogy.plugins.preprocess',
 'dialogy.plugins.preprocess.text',
 'dialogy.types',
 'dialogy.types.entity',
 'dialogy.types.intent',
 'dialogy.types.plugin',
 'dialogy.types.signal',
 'dialogy.types.slots',
 'dialogy.types.utterances',
 'dialogy.utils',
 'dialogy.workflow']

package_data = \
{'': ['*']}

install_requires = \
['attrs>=20.3.0,<21.0.0',
 'coloredlogs>=15.0,<16.0',
 'copier>=5.1.0,<6.0.0',
 'docopt>=0.6.2,<0.7.0',
 'numpy>=1.20.2,<2.0.0',
 'pydash>=4.9.3,<5.0.0',
 'python-dateutil>=2.8.1,<3.0.0',
 'pytz>=2020.4,<2021.0',
 'requests>=2.25.1,<3.0.0',
 'scipy>=1.7.1,<2.0.0',
 'watchdog>=1.0.2,<2.0.0']

entry_points = \
{'console_scripts': ['dialogy = dialogy.cli:main']}

setup_kwargs = {
    'name': 'dialogy',
    'version': '0.7.4',
    'description': 'Language understanding for human dialog.',
    'long_description': None,
    'author': 'Amresh Venugopal',
    'author_email': 'amresh.venugopal@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
