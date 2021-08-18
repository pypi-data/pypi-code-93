# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['hs',
 'hs.cli',
 'hs.cli.commands',
 'hs.entities',
 'hs.metadata_collectors',
 'hs.util']

package_data = \
{'': ['*']}

install_requires = \
['GitPython>=3.1.18,<4.0.0',
 'click-aliases>=1.0.1,<1.1.0',
 'click-log>=0.3,<0.4',
 'click>=7.1.2,<7.2.0',
 'hydrosdk==3.0.0a10',
 'kafka-python==1.4.3',
 'protobuf>=3.6,<4.0',
 'pydantic-yaml>=0.4.0,<0.5.0',
 'requests-toolbelt>=0.9,<0.10',
 'requests>=2.23.0,<2.24.0',
 'sseclient-py>=1.7,<1.8',
 'tabulate>=0.8,<0.9']

entry_points = \
{'console_scripts': ['hs = hs.cli.commands.hs:hs_cli']}

setup_kwargs = {
    'name': 'hs',
    'version': '3.0.0a19',
    'description': 'Hydro-serving command line tool',
    'long_description': None,
    'author': 'Hydrospheredata',
    'author_email': None,
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
