# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['labthings',
 'labthings.actions',
 'labthings.apispec',
 'labthings.default_views',
 'labthings.default_views.docs',
 'labthings.example_components',
 'labthings.json',
 'labthings.json.marshmallow_jsonschema',
 'labthings.marshalling',
 'labthings.sync',
 'labthings.views']

package_data = \
{'': ['*'], 'labthings.default_views.docs': ['static/*', 'templates/*']}

install_requires = \
['Flask>=1.1.1,<2.0.0',
 'apispec[validation,yaml]>=3.2,<5.0',
 'apispec_webframeworks>=0.5.2,<0.6.0',
 'flask-cors>=3.0.8,<4.0.0',
 'marshmallow>=3.4.0,<4.0.0',
 'webargs>=6,<9',
 'zeroconf>=0.24.5,<0.34.0']

setup_kwargs = {
    'name': 'labthings',
    'version': '1.3.2',
    'description': 'Python implementation of LabThings, based on the Flask microframework',
    'long_description': '# Python LabThings (for Flask)\n\n[![LabThings](https://img.shields.io/badge/-LabThings-8E00FF?style=flat&logo=data:image/svg+xml;base64,PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiPz4NCjwhRE9DVFlQRSBzdmcgIFBVQkxJQyAnLS8vVzNDLy9EVEQgU1ZHIDEuMS8vRU4nICAnaHR0cDovL3d3dy53My5vcmcvR3JhcGhpY3MvU1ZHLzEuMS9EVEQvc3ZnMTEuZHRkJz4NCjxzdmcgY2xpcC1ydWxlPSJldmVub2RkIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiIHN0cm9rZS1taXRlcmxpbWl0PSIyIiB2ZXJzaW9uPSIxLjEiIHZpZXdCb3g9IjAgMCAxNjMgMTYzIiB4bWw6c3BhY2U9InByZXNlcnZlIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPjxwYXRoIGQ9Im0xMjIuMjQgMTYyLjk5aDQwLjc0OHYtMTYyLjk5aC0xMDEuODd2NDAuNzQ4aDYxLjEyMnYxMjIuMjR6IiBmaWxsPSIjZmZmIi8+PHBhdGggZD0ibTAgMTIuMjI0di0xMi4yMjRoNDAuNzQ4djEyMi4yNGg2MS4xMjJ2NDAuNzQ4aC0xMDEuODd2LTEyLjIyNGgyMC4zNzR2LTguMTVoLTIwLjM3NHYtOC4xNDloOC4wMTl2LTguMTVoLTguMDE5di04LjE1aDIwLjM3NHYtOC4xNDloLTIwLjM3NHYtOC4xNWg4LjAxOXYtOC4xNWgtOC4wMTl2LTguMTQ5aDIwLjM3NHYtOC4xNWgtMjAuMzc0di04LjE0OWg4LjAxOXYtOC4xNWgtOC4wMTl2LTguMTVoMjAuMzc0di04LjE0OWgtMjAuMzc0di04LjE1aDguMDE5di04LjE0OWgtOC4wMTl2LTguMTVoMjAuMzc0di04LjE1aC0yMC4zNzR6IiBmaWxsPSIjZmZmIi8+PC9zdmc+DQo=)](https://github.com/labthings/)\n[![ReadTheDocs](https://readthedocs.org/projects/python-labthings/badge/?version=latest&style=flat)](https://python-labthings.readthedocs.io/en/latest/)\n[![PyPI](https://img.shields.io/pypi/v/labthings)](https://pypi.org/project/labthings/)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n[![codecov](https://codecov.io/gh/labthings/python-labthings/branch/master/graph/badge.svg)](https://codecov.io/gh/labthings/python-labthings)\n[![Riot.im](https://img.shields.io/badge/chat-on%20riot.im-368BD6)](https://riot.im/app/#/room/#labthings:matrix.org)\n\nA thread-based Python implementation of the LabThings API structure, based on the Flask microframework.\n\n## Installation\n\n`pip install labthings`\n\n## Quickstart example\n\nThis example assumes a `PretendSpectrometer` class, which already has `data` and `integration_time` attributes, as well as an `average_data(n)` method. LabThings allows you to easily convert this existing instrument control code into a fully documented, standardised web API complete with auto-discovery and automatic background task threading.\n\n```python\n#!/usr/bin/env python\nimport time\n\nfrom labthings import ActionView, PropertyView, create_app, fields, find_component, op\nfrom labthings.example_components import PretendSpectrometer\nfrom labthings.json import encode_json\n\n"""\nClass for our lab component functionality. This could include serial communication,\nequipment API calls, network requests, or a "virtual" device as seen here.\n"""\n\n\n"""\nCreate a view to view and change our integration_time value,\nand register is as a Thing property\n"""\n\n\n# Wrap in a semantic annotation to automatically set schema and args\nclass DenoiseProperty(PropertyView):\n    """Value of integration_time"""\n\n    schema = fields.Int(required=True, minimum=100, maximum=500)\n    semtype = "LevelProperty"\n\n    @op.readproperty\n    def get(self):\n        # When a GET request is made, we\'ll find our attached component\n        my_component = find_component("org.labthings.example.mycomponent")\n        return my_component.integration_time\n\n    @op.writeproperty\n    def put(self, new_property_value):\n        # Find our attached component\n        my_component = find_component("org.labthings.example.mycomponent")\n\n        # Apply the new value\n        my_component.integration_time = new_property_value\n\n        return my_component.integration_time\n\n\n"""\nCreate a view to quickly get some noisy data, and register is as a Thing property\n"""\n\n\nclass QuickDataProperty(PropertyView):\n    """Show the current data value"""\n\n    # Marshal the response as a list of floats\n    schema = fields.List(fields.Float())\n\n    @op.readproperty\n    def get(self):\n        # Find our attached component\n        my_component = find_component("org.labthings.example.mycomponent")\n        return my_component.data\n\n\n\n"""\nCreate a view to start an averaged measurement, and register is as a Thing action\n"""\n\n\nclass MeasurementAction(ActionView):\n    # Expect JSON parameters in the request body.\n    # Pass to post function as dictionary argument.\n    args = {\n        "averages": fields.Integer(\n            missing=20, example=20, description="Number of data sets to average over",\n        )\n    }\n    # Marshal the response as a list of numbers\n    schema = fields.List(fields.Number)\n\n    # Main function to handle POST requests\n    @op.invokeaction\n    def post(self, args):\n        """Start an averaged measurement"""\n\n        # Find our attached component\n        my_component = find_component("org.labthings.example.mycomponent")\n\n        # Get arguments and start a background task\n        n_averages = args.get("averages")\n\n        # Return the task information\n        return my_component.average_data(n_averages)\n\n\n# Create LabThings Flask app\napp, labthing = create_app(\n    __name__,\n    title="My Lab Device API",\n    description="Test LabThing-based API",\n    version="0.1.0",\n)\n\n# Attach an instance of our component\n# Usually a Python object controlling some piece of hardware\nmy_spectrometer = PretendSpectrometer()\nlabthing.add_component(my_spectrometer, "org.labthings.example.mycomponent")\n\n\n# Add routes for the API views we created\nlabthing.add_view(DenoiseProperty, "/integration_time")\nlabthing.add_view(QuickDataProperty, "/quick-data")\nlabthing.add_view(MeasurementAction, "/actions/measure")\n\n\n# Start the app\nif __name__ == "__main__":\n    from labthings import Server\n\n    Server(app).run()\n```\n\n## Acknowledgements\n\nMuch of the code surrounding default response formatting has been liberally taken from [Flask-RESTful](https://github.com/flask-restful/flask-restful). The integrated [Marshmallow](https://github.com/marshmallow-code/marshmallow) support was inspired by [Flask-Marshmallow](https://github.com/marshmallow-code/flask-marshmallow) and [Flask-ApiSpec](https://github.com/jmcarp/flask-apispec). \n\n## Developer notes\n\n### Changelog generation\n\n* `npm install -g conventional-changelog-cli`\n* `npx conventional-changelog -r 1 --config ./changelog.config.js -i CHANGELOG.md -s`\n',
    'author': 'Joel Collins',
    'author_email': 'joel@jtcollins.net',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/labthings/python-labthings/',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
