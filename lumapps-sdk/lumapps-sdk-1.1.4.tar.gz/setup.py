# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['lumapps', 'lumapps.api', 'lumapps.api.helpers']

package_data = \
{'': ['*']}

install_requires = \
['Authlib<=0.15.3',
 'PyJWT>=2.1.0,<3.0.0',
 'httpx',
 'pre-commit>=2.13.0,<3.0.0',
 'python-slugify>=4.0.1,<5.0.0']

entry_points = \
{'console_scripts': ['lac = lumapps.api.cli:main']}

setup_kwargs = {
    'name': 'lumapps-sdk',
    'version': '1.1.4',
    'description': '',
    'long_description': '# Lumapps SDK\n\n<p align="center">\n    <a href="https://github.com/lumapps/lumapps-sdk/actions?query=workflow%3ACI"><img alt="Action Status" src="https://github.com/lumapps/lumapps-sdk/workflows/CI/badge.svg"></a>\n    <a href="https://pypi.org/project/lumapps-sdk/"><img alt="Pypi" src="https://img.shields.io/pypi/v/lumapps-sdk"></a>\n    <a href="https://codecov.io/gh/lumapps/lumapps-sdk/branch/master"><img alt="Coverage" src="https://codecov.io/gh/lumapps/lumapps-sdk/branch/master/graph/badge.svg"></a>\n    <a href="https://github.com/ambv/black"><img alt="Black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>\n    <a href="#"><img alt="Black" src="https://img.shields.io/badge/python-3.6%7C3.7%7C3.8-blue"></a>\n</p>\n\n\nLumApps SDK is a set of tools to manipulate the [LumApps API](https://api.lumapps.com/docs/start)\n\nThis includes:\n\n- A client that support all the routes of the API (located in folder lumapps)\n- A set of helper classes to easily manipulate LumApps elements as Python Objects and classes (folder lumapps/helpers)\n\n\n## Installation\n\n\n```bash\npip install lumapps-sdk\n```\n\n## Getting started\n\n\n1. Get your token\n\n    LumApps supports multiple ways of authentication.\n    The fastest one to implement is the following:\n\n    Get your token by logging to your LumApps account.\n    Go to [https://sites.lumapps.com](https://sites.lumapps.com) and authenticate.\n    Once connected, open the javascript console of your browser and run:\n\n    ```javascript\n    var instance = window.location.pathname.split(\'/\');\n    instance = instance[1] == "a" ? instance[3] : instance[1]\n    fetch(window.location.origin+"/service/init?customerHost="+window.location.host+"&instanceSlug="+instance+"&    slug=").then(data=>{return data.json()}).then(res => {console.log(res.token)})\n    ```\n\n    This will generate your personal LumApps token that will be active for 60 minutes, and that we will use in the following steps\n\n2. Authenticate\n\n    ```python\n    from lumapps.api import BaseClient\n\n    token = "MY TOKEN"\n    client = BaseClient(token=token)\n    ```\n\n3. Make your first API call\n\n    Let\'s display the full name of a registered user in lumapps\n\n    ```python\n    user_email = "YOUR EMAIL"\n    usr = api.get_call("user/get", email=user_email)\n    print("Hello {}".format(usr["fullName"]))\n    ```\n\n## Documentation\n\nThe SDK documentation is available [here](https://lumapps.github.io/lumapps-sdk/).\n\n## Code convention\n\nDocstring in PEP 484 type annotations format adapted to python 2.7 using comments.\n\n## How to get help, contribute, or provide feedback\n\nPlease refer to our [contributing guidelines](CONTRIBUTING.md).\n\n## Copyright and license\n\n\nLumApps SDK is released under the [MIT license](LICENSE.md).\n\n\n',
    'author': 'Aurélien Dentan',
    'author_email': 'aurelien@lumapps.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/lumapps/lumapps-sdk',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6.4,<4.0.0',
}


setup(**setup_kwargs)
