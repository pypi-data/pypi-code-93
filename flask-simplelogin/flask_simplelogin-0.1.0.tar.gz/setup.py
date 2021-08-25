# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['flask_simplelogin']

package_data = \
{'': ['*'], 'flask_simplelogin': ['templates/*']}

install_requires = \
['Flask-WTF>=0.15.1,<0.16.0', 'Flask>=0.12', 'click>=8.0.1,<9.0.0']

setup_kwargs = {
    'name': 'flask-simplelogin',
    'version': '0.1.0',
    'description': 'Flask Simple Login - Login Extension for Flask',
    'long_description': "[![GitHub Actions](https://img.shields.io/github/workflow/status/flask-extensions/Flask-SimpleLogin/Tests?style=flat-square)](https://github.com/flask-extensions/Flask-SimpleLogin/actions/workflows/tests.yml)\n[![PyPI](https://img.shields.io/pypi/v/flask_simplelogin.svg?style=flat-square)](https://pypi.org/project/flask_simplelogin/)\n[![PyPI versions](https://img.shields.io/pypi/pyversions/flask_simplelogin.svg?style=flat-square)](https://pypi.org/project/flask_simplelogin/)\n[![PyPI formats](https://img.shields.io/pypi/format/flask_simplelogin.svg?style=flat-square)](https://pypi.org/project/flask_simplelogin/)\n[![Flask](https://img.shields.io/badge/Flask-Extension-blue.svg?style=flat-square)](https://github.com/pallets/flask)\n[![Documentation](https://img.shields.io/readthedocs/flask-simple-login?style=flat-square)](https://flask-simple-login.readthedocs.io/en/latest/?badge=latest)\n\n# Login Extension for Flask\n\nThe simplest way to add login to flask!\n\n## How it works\n\nFirst, install it from [PyPI](https://pypi.org/project/flask_simplelogin/):\n\n```console\n$ pip install flask_simplelogin\n```\n\nThen, use it in your app:\n\n```python\nfrom flask import Flask\nfrom flask_simplelogin import SimpleLogin\n\napp = Flask(__name__)\nSimpleLogin(app)\n```\n\n## **That's it!**\n\nNow you have `/login` and `/logout` routes in your application.\n\nThe username defaults to `admin` and the password defaults to `secret` — yeah that's not clever, check the [docs](https://flask-simple-login.readthedocs.io/en/latest/?badge=latest) to see how to configure it properly!\n\n![Login Screen](./login_screen.png)\n\nCheck the [documentation](https://flask-simple-login.readthedocs.io/en/latest/?badge=latest) for more details!\n",
    'author': 'Bruno Rocha',
    'author_email': 'rochacbruno@users.noreply.github.com',
    'maintainer': 'Eduardo Cuducos',
    'maintainer_email': 'cuducos@users.noreply.github.com',
    'url': 'https://github.com/flask-extensions/Flask-SimpleLogin',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
