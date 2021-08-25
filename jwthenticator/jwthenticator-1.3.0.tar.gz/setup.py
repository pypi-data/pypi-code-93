# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['jwthenticator']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.6.0,<4.0.0',
 'asyncalchemy>=1.1.1,<2.0.0',
 'cryptography>=2.8,<4.0.0',
 'environs>=9.3.1,<10.0.0',
 'marshmallow-dataclass>=8.3,<9.0',
 'marshmallow>=3.9,<4.0',
 'pg8000==1.16.5',
 'pycryptodomex>=3.9,<4.0',
 'pyjwt>=1.7,<3.0.0',
 'sqlalchemy-utils>=0.33.0,<1.0.0',
 'sqlalchemy>=1.2.19,<1.4.0']

extras_require = \
{':python_version >= "3.6" and python_version < "3.7"': ['dataclasses>=0.7,<0.8']}

setup_kwargs = {
    'name': 'jwthenticator',
    'version': '1.3.0',
    'description': 'A cloud first service for key to JWT authentication library and server written in Python 3.',
    'long_description': '# JWThenticator\nA cloud first service for key to JWT authentication library and server written in Python 3.\n\n\n## Intro\nJWThenticator was written for client authentication in micro-services architectures with usage of API gateways in mind.\\\nAlthough there are multiple open-source projects for authenticating users in exchange for JWT (json web token), we couldn\'t find any project that fit our need for a key based authentication for our clients. This is beneficial for any client authentication and more specifically for IoT.\\\nThe service is stateless, Docker first service for cloud authentication, but can generally be used for any key to JWT authentication and in multiple different architectures (see example [below](#example-architecture)).\n\n\n## How To Use\n### Pip\n```bash\npip install jwthenticator\n```\nTo run as a server you can run: `python3 -m jwthenticator.server`.\\\nMake sure to configure the proper database to be used via the environment variables exposed in [jwthenticator/consts.py](jwthenticator/consts.py) file.\\\nBy default PostgreSQL is used and a basic local config setup is:\n```bash\nexport DB_USER="my-postgres-user"\nexport DB_PASS="my-postgres-pass"\n```\nNote - if RSA keys are not provided (via the environment variables `RSA_PUBLIC_KEY` + `RSA_PRIVATE_KEY` or `RSA_PUBLIC_KEY_PATH` + `RSA_PRIVATE_KEY_PATH`), a new RSA pair will be generated every time the systems goes up.\n\n### Docker\n```bash\ndocker pull clarotyltd/jwthenticator\ndocker run -p 8080:8080 clarotyltd/jwthenticator\n```\nA database is needed to be linked or configured to the image.\\\nSee [examples/docker-compose.yml](examples/docker-compose.yml) for a full example, run it using:\n```bash\ncd examples\ndocker-compose up\n```\n\n### From Source\nThe project uses [poetry](https://github.com/python-poetry/poetry) for dependency management and packaging.\\\nTo run from source clone project and:\n```bash\npip install poetry\npoetry install\n```\n\n\n## Documentation\n- API documentation - [openapi.yaml](openapi.yaml) file (ex Swagger)\n- Configurable environment variables - [jwthenticator/consts.py](jwthenticator/consts.py)\n- Code usage examples - [Code Examples](#code-examples)\n- Example architecture - [Example Architecture](#example-architecture)\n- Diagrams - [docs](docs) folder for some UML [sequence diagrams](https://sequencediagram.org/) and Python diagrams using [diagrams](https://github.com/mingrammer/diagrams)\n\n\n## Code Examples\nFor full examples see the [examples](jwthenticator/examples) folder.\n\n### Client\nTo make it easier to work agains a JWThenticator protected server (either directly or via API gateway), a client class is provided.\\\nThe `Client` class handles auth state management against JWThenticator. It handles JWthenticator responses for you, performs authentication for you, and JWT refresh when needed.\\\nIt exposes a `request_with_auth` function (and the simpler `get_with_auth` and `post_with_auth`) that manages all interactions against the secured service and the JWThenticator itself for you.\\\nExample usage:\n```python\nfrom uuid import uuid4\nfrom jwthenticator.client import Client\n\nidentifier = uuid4()\nclient = Client("https://my-jwthenticator-host/", identifier, key="my-awesome-key")\nresponse = await client.get_with_auth("https://my-secure-server/")\n```\n\n### Server\nAlthough JWThenticator was designed with an API gateway in mind, it can be used to authenticate server endpoints directly.\\\nFor easy usage with an [aiohttp](https://docs.aiohttp.org/en/stable/) Python server you can do the following:\n```python\nfrom aiohttp import web\nfrom jwthenticator.server_utils import authenticate\n\napp = web.Application()\n\n@authenticate("https://my-jwthenticator-host/")\nasync def secure_index(request: web.Request) -> web.Response:\n    return "Secure hello world!"\n\napp.add_routes([web.get("/", secure_index)])\nweb.run_app(app)\n```\n\n\n## Example Architecture\nA visual example on how JWThenticator is and can be used.\\\nAdditional ones can be found in [docs](docs) folder.\n\n### API Gateway Architecture\nGenerated from [docs/api_gateway_architecture_diagram.py](docs/api_gateway_architecture_diagram.py)\\\n![API Gateway Architecture](https://user-images.githubusercontent.com/3015856/103092541-3cdd1c00-4600-11eb-807d-6033f6fdfa72.png)\n\n### API Gateway REST Sequence Diagram\nGenerated from [docs/api_gateway_flow.diag](docs/api_gateway_flow.diag)\\\n![API Gateway REST Sequence Diagram](https://user-images.githubusercontent.com/3015856/103092521-2931b580-4600-11eb-8a0e-a4fb7ccf41c0.png)\n\n## How it works\nThere are 3 key components to JWThenticator:\n\n### Keys\nKeys that are registered against the service and can then be used for authentication.\\\nAll keys are registered to the database, have an expiration time (change default of 30 minutes using the env var `KEY_EXPIRY` in seconds), identifier of the registrant and some other metadata stored about them.\\\nThe identifier is usefull if a key needs to be linked later to a specific server or route.\n\n### Refresh tokens\nSince JWTs are short lived and keys should be kept safe, an intermediate method is needed so we don\'t have a long lived JWTs or use our secret key every 30 minutes (by default). This is where refresh token come into play.\\\nRefresh tokens are received from a successfull authentication and are used for receiving a new JWTs after they expire.\\\nThey are recoreded in the database, have an expiration time (change default of 60 days using  the env var `REFRESH_TOKEN_EXPIRY` in seconds) and some other metadata stored about them.\\\nYou can check out [jwthenticator/models.py](jwthenticator/models.py) to see what data is stored in the database.\n\n### JWTs\nThe industry standard JWT ([RFC 7519](https://tools.ietf.org/html/rfc7519)). The JWT is used for verification against an API gateway, JWThenticator itself, or any service / code you use for you auth verification.\\\nThe JWTs are short lived (as they should be) with a configurable lease time via `JWT_LEASE_TIME` env var.\\\nAdditionaly, similarly to the keys we use a UUID identifier in the authentication process and store it in the JWT\'s payload. This is useful for better client identification or smarter k8s routing.\n\n\n## Addtional Features\n- All consts can be overriden via environment variables, see [jwthenticator/consts.py](jwthenticator/consts.py) for the full list.\n- Service contains both internal and public routes, the admin / public API\'s can be disabled by setting the `DISABLE_EXTERNAL_API` or `DISABLE_INTERNAL_API` env vars. This is very important when running the service in production environments, you don\'t want to expose the key registration to the general public :).\n- The service can be used with any JWT verification service or API gateway using the industry standard JWKS ([RFC 7517](https://tools.ietf.org/html/rfc7517)) via `/jwks` API call.\n- JWThenticator can be used as an [Nginx authentication](http://nginx.org/en/docs/http/ngx_http_auth_request_module.html) backend using the `/validate_request` API call.\n- Some requests require giving a UUID identifier. Even though the service doesn\'t enforce its verification, it can be used as a mean of identifiying incoming users, smart routing, and later for additional validations.\n- All REST API schemas are defined using Python `dataclass`es and validated using [marshmallow_dataclass](https://github.com/lovasoa/marshmallow_dataclass), see [schemas.py](jwthenticator/schemas.py).\n',
    'author': 'Guy Zylberberg',
    'author_email': 'guyzyl@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/claroty/jwthenticator',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
