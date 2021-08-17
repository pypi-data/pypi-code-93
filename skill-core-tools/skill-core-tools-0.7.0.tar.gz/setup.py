# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['skill_core_tools', 'skill_core_tools.downloader', 'skill_core_tools.uploader']

package_data = \
{'': ['*']}

entry_points = \
{'console_scripts': ['build = poetry_scripts:build',
                     'install = poetry_scripts:install',
                     'publish = poetry_scripts:publish',
                     'release = poetry_scripts:release',
                     'test = poetry_scripts:test']}

setup_kwargs = {
    'name': 'skill-core-tools',
    'version': '0.7.0',
    'description': '',
    'long_description': None,
    'author': 'Leftshift One Software GmbH',
    'author_email': 'devs@leftshift.one',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
