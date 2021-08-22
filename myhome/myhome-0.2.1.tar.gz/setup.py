# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['myhome',
 'myhome._gen',
 'myhome._gen.api',
 'myhome._gen.apis',
 'myhome._gen.model',
 'myhome._gen.models',
 'myhome._gen.test',
 'myhome.object']

package_data = \
{'': ['*']}

install_requires = \
['urllib3>=1.26.2']

setup_kwargs = {
    'name': 'myhome',
    'version': '0.2.1',
    'description': 'Python client library for interacting with Bticino MMYHOMESERVER1',
    'long_description': '# myhome\n\n*myhome* is a Python package providing an API client for the Legrand/Bticino MyHomeSERVER1 API.\n\nThis API is usually used by the *MyHome_UP* mobile application and has been partially\nreverse-engineered from intercepting the traffic between the application and the server\nrunning on the local network. You can find information on the [analysis setup](doc/analysis_setup.md)\nand the [API](doc/api.md) itself in the *doc* directory of this repository.\n\nPlease be aware that this is a very early version of the library and things may change at any\npoint in time.\nThe long-term goal is to implement a library with a stable interface which can then be\nused in home automation systems and frameworks, like *Home Assistant*.\n\n## OpenAPI spec\n\nThis repository contains an [OpenAPI spec](contrib/openapi.yml) which partially describes\nthe API exposed by MyHomeSERVER1.\n\n## Status\n\n- [x] Basic light control\n- [x] Basic dimmer control\n- [x] Basic shutter control\n- [x] Basic thermostat control\n- [x] Basic room support\n- [x] Basic zone support\n- [x] CI pipeline\n- [ ] Unit tests\n- [ ] Library documentation\n',
    'author': 'Stephan Peijnik-Steinwender',
    'author_email': 'speijnik@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/speijnik/myhome',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
