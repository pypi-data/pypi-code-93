# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ask_lang',
 'ask_lang.tests',
 'ask_lang.tests.transpiler',
 'ask_lang.tests.transpiler.utilities',
 'ask_lang.tests.utilities',
 'ask_lang.transpiler',
 'ask_lang.transpiler.utilities',
 'ask_lang.utilities']

package_data = \
{'': ['*']}

install_requires = \
['Flask-Cors>=3.0.10,<4.0.0',
 'Flask-Limiter>=1.4,<2.0',
 'Flask-Mail>=0.9.1,<0.10.0',
 'Flask-SQLAlchemy>=2.4.4,<3.0.0',
 'Flask-Selfdoc>=1.2.3,<2.0.0',
 'Flask>=1.1.2,<2.0.0',
 'Jinja2>=2.11.3,<3.0.0',
 'Paste>=3.5.0,<4.0.0',
 'PyJWT==1.7.1',
 'PyMySQL>=1.0.2,<2.0.0',
 'SQLAlchemy>=1.3.23,<2.0.0',
 'abnex==1.0.2',
 'coverage>=5.5,<6.0',
 'limits>=1.5.1,<2.0.0',
 'requests>=2.25.1,<3.0.0',
 'six>=1.15.0,<2.0.0',
 'tabulate>=0.8.8,<0.9.0',
 'toml>=0.10.2,<0.11.0',
 'waitress>=1.4.4,<2.0.0']

entry_points = \
{'console_scripts': ['ask = ask_lang:main']}

setup_kwargs = {
    'name': 'ask-lang',
    'version': '1.4.2',
    'description': 'Ask is a modern open-source transpiled programming language, designed for building backend services and APIs. Ask reduces the amount of needed boilerplate code for setting up things like database connections and authentication to virtually zero lines.',
    'long_description': '<img src="https://ask.edvard.dev/banner.png" alt="Ask">\n\n# Ask\n\n[![CircleCI](https://circleci.com/gh/circleci/circleci-docs.svg?style=svg)](https://circleci.com/gh/Buscedv/Ask)\n\n## Introduction.\nAsk is an open source, dynamic, and transpiled programming language built for building backends and APIs. Ask directly transpiles to Python, more specifically Flask.\n\n### Feature Highlights\n- Built-in JWT Authentication.\n- Super Simple Database Management.\n- Syntax Inspired by Python.\n- Built-in CORS Support.\n- Reduces Boilerplate.\n- Compatible with Python*\n\n`* = You can import external Python modules and call them from you Ask code.`\n\n## Easy to Learn\nAsk\'s syntax is heavily inspired by Python, and can almost be considered to be a superset of Python. This means that picking up Ask is super easy if you’re already familiar with Python.\n\nThe main idea behind Ask is to simplify common backend actions (e.g. working with databases). Building a full database CRUD REST API with JWT authentication in Ask is very straight forward and simple and requires virtually zero lines of boilerplate code and no setup whatsoever.\n\n## Extendable.\nAsk is a transpiled language (kind of like TypeScript) which means that it compiles the source code to another language that has a similar level of abstraction. In Ask\'s case, the target language is Python, more specifically a Flask app.\n\nFlask is a very popular and well-established web framework for Python, so there\'s already a lot of tools, and services for deploying Flask apps.\n\nThe transpiled app is completely standalone and doesn\'t require Ask in any way.\n\n## Installation (normal usage)\n- You can install Ask from the PyPI. You can use `pip` but we recommend that you use [pipx](https://pipxproject.github.io/pipx/).\n- `$ pipx install ask-lang`.\n- Then run your apps with: `$ ask [your file].ask`.\n\n## Run locally (for development)\n1. Clone this repo: `https://github.com/Buscedv/Ask.git`.\n2. Install [Poetry](https://python-poetry.org/).\n3. Create a new virtual environment: `python3 venv venv`.\n4. Activate it: `source venv/bin/activate`.\n5. Install dependencies: `poetry install`.\n6. (Optional but helpful in some cases) Run Ask in development mode: [Docs](https://docs.ask-lang.org/development-tools/running-in-development-mode1).\n\nIf you want to contribute please read the CONTRIBUTING.md file for code style, standards, etc.\n\n## Example (Ask vs Flask)\nHere is the same basic app with one GET route written in Ask and in Python with Flask.\n\n### Ask\n```python\nproducts = [\n  {\n    name: \'Product 1\',\n    price: 30.0,\n    qty: 300\n  },\n  {\n    name: \'Product 2\',\n    price: 15.5,\n    qty: 20\n  }\n]\n\n@get(\'/api/v1/products\'):\n  respond({products: products})\n```\n\n### Flask\nThis is what the same application would look like in Flask.\n\n```python\nfrom flask import Flask, jsonify\n\napp = Flask(__name__)\n\nproducts = [\n  {\n    \'name\': \'Product 1\',\n    \'price\': 30.0,\n    \'qty\': 300\n  },\n  {\n    \'name\': \'Product 2\',\n    \'price\': 15.5,\n    \'qty\': 20\n  }\n]\n\n@app.route(\'/api/v1/products\', methods=[\'GET\'])\ndef get_products():\n  return jsonify({\'products\': products})\n\nif __name__ == \'__main__\':\n  app.run()\n```\n\nAs you can see Ask hides away all the clutter and boilerplate.\n\n## Documentation\nYou can find the full documentation on [docs.ask-lang.org](https://docs.ask-lang.org).\n\n## Contact\n- Website: [ask-lang.org](https://ask-lang.org).\n- Email: [me(a)edvard.dev](mailto:me@edvard.dev).\n- GitHub: [Buscedv](https://github.com/Buscedv).\n',
    'author': 'Edvard Busck-Nielsen',
    'author_email': 'me@edvard.dev',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://ask-lang.org',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
