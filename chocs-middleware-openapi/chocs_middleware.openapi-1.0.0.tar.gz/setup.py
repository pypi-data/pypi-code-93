# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['chocs_middleware', 'chocs_middleware.openapi']

package_data = \
{'': ['*']}

install_requires = \
['chocs>=1.0.0-beta.0,<2.0.0', 'opyapi>=1.0.0,<2.0.0']

setup_kwargs = {
    'name': 'chocs-middleware.openapi',
    'version': '1.0.0',
    'description': 'Middleware to validate incoming requests with openapi spec.',
    'long_description': '# Chocs-OpenApi <br> [![CI](https://github.com/kodemore/chocs-openapi/actions/workflows/main.yaml/badge.svg?branch=main)](https://github.com/kodemore/chocs-openapi/actions/workflows/main.yaml) [![Release](https://github.com/kodemore/chocs-openapi/actions/workflows/release.yml/badge.svg?branch=main)](https://github.com/kodemore/chocs-openapi/actions/workflows/release.yml) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)\nOpenApi middleware for chocs library.\n\nNewest OpenAPI Specification (v.3.x) can be easily integrated into Chocs through application\'s middleware. \nValidation is performed via [JsonSchema Draft-7.0 specification](https://json-schema.org) and all commonly \nused features are supported.\n\n## Features\n\nOpen api integration can be used to:\n- validate request\'s body\n- validate request\'s path parameters\n- validate request\'s headers\n- validate request\'s query parameters\n- validate request\'s cookies  \n- json references\n\n## Installation\n\nWith pip,\n```shell\npip install chocs-middleware.openapi\n```\nor through poetry\n```shell\npoetry add chocs-middleware.openapi\n```\n\n# Usage\n\n## Using your OpenAPI file\n\nChocs can read json and yaml files, this example will cover yaml usage although the only difference is the file extension.\n\n```python\nimport chocs\nfrom chocs_middleware.openapi import OpenApiMiddleware\nfrom os import path\n\n# absolute path to file containing open api documentation; yaml and json files are supported\nopenapi_filename = path.join(path.dirname(__file__), "/openapi.yml")\n\n# instantiating application and passing open api middleware\napp = chocs.Application(OpenApiMiddleware(openapi_filename, validate_body=True, validate_query=True))\n\n# the registered route must correspond to open api route within `path` section.\n# if request body is invalid the registered controller will not be invoked\n@app.post("/pets")\ndef create_pet(request: chocs.HttpRequest) -> chocs.HttpResponse:\n  ...\n  return chocs.HttpResponse(status=200)\n```\nComplete integration example can be [found here](./examples/input_validation_with_open_api/openapi.yml)\n\n> Keep in mind registered route has to match 1:1 the specified route inside `paths` section inside your OpenApi documentation\n\n## Validating request body\n\nBelow is very simple schema to validate request body of a `POST /pet` request. Request body is required, should be valid json request and contain the following properties:\n- name (string)\n- tags (array of string)\n- id (optional string)\n\n`openapi.yml`\n```yaml\nopenapi: "3.0.0"\ninfo:\n  version: "1.0.0"\n  title: "Pet Store"\npaths:\n  /pets:\n    post:\n      description: Creates a new Pet\n      requestBody:\n        description: Pet\n        required: true\n        content:\n          application/json:\n            schema:\n              $ref: "#/components/schemas/Pet"\n      responses:\n        200:\n          description: "Success"\ncomponents:\n  schemas:\n    Pet:\n      type: object\n      required:\n        - name\n        - tag\n      properties:\n        id:\n          type: integer\n        name:\n          type: string\n        tag:\n          type: array\n          items:\n            type: string\n```\n\n`app.py`\n```python\nimport chocs\nfrom chocs_middleware.openapi import OpenApiMiddleware\nfrom os import path\n\nopenapi_filename = path.join(path.dirname(__file__), "/openapi.yml")\napp = chocs.Application(OpenApiMiddleware(openapi_filename, validate_body=True))\n\n@app.post("/pets")\ndef create_pet(request: chocs.HttpRequest) -> chocs.HttpResponse:\n  pet = request.parsed_body # here we will get valid pet\n  return chocs.HttpResponse(status=200)\n\nchocs.serve(app)\n```\n\n`create_pet` controller will be only invoked if request contains valid body. Pet\'s data can be accessed through `request.parsed_body` which is a dict-like object.\n\n## Json schema support\n\nChocs uses JSON Schema to validate your open api definitions with full draft-7 support and almost complete 2019-09 standard support. \nThis means you can use almost every feature described on the [understanding json schema](https://json-schema.org/understanding-json-schema/reference/index.html) webpage. \nThe webpage is a great resource full of examples and detailed descriptions around JSON Schema. \n\n\n> There are some caveats around `allOf` validator:\n> - all object schemas inside `allOf` definition are automatically composed into a single object definition\n> - when combining string validators make sure format validator is the last validator in the pipeline otherwise validation might fail due to string casting\n\n',
    'author': 'Dawid Kraczkowski',
    'author_email': 'dawid.kraczkowski@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/kodemore/chocs-openapi',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
