# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['rashsetup',
 'rashsetup.RashScrappers',
 'rashsetup.RashScrappers.RashScrappers',
 'rashsetup.RashScrappers.RashScrappers.spiders',
 'rashsetup.__RashModules__',
 'rashsetup.__RashModules__.Rash',
 'rashsetup.__RashModules__.RashLogger']

package_data = \
{'': ['*'],
 'rashsetup.RashScrappers': ['RashScrappers/spiders/temp/*'],
 'rashsetup.__RashModules__': ['Rash/Misc/CSS/*',
                               'Rash/Misc/Gifs/*',
                               'Rash/Misc/HTML/*',
                               'Rash/Misc/HTML/TextBrowser/*',
                               'Rash/Misc/HTML/WebEngineView/*',
                               'Rash/Misc/Icons/*',
                               'Rash/Misc/UI/*']}

setup_kwargs = {
    'name': 'rashsetup',
    'version': '0.5.2',
    'description': 'Setup Module that can be used for both testing Rash and also Setting up Rash',
    'long_description': None,
    'author': 'Rahul',
    'author_email': 'saihanumarahul66@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
