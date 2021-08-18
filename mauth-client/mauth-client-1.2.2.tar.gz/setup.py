# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mauth_client',
 'mauth_client.flask_authenticator',
 'mauth_client.lambda_authenticator',
 'mauth_client.requests_mauth']

package_data = \
{'': ['*']}

install_requires = \
['cachetools>=4.1,<5.0', 'requests>=2.23,<3.0', 'rsa>=4.0,<5.0']

extras_require = \
{':python_version < "3.8"': ['importlib-metadata>=1.0,<2.0']}

setup_kwargs = {
    'name': 'mauth-client',
    'version': '1.2.2',
    'description': 'MAuth Client for Python',
    'long_description': '# MAuth Client Python\n[![Build\nStatus](https://travis-ci.com/mdsol/mauth-client-python.svg?token=YCqgqZjJBpwz6GCprYaV&branch=develop)](https://travis-ci.com/mdsol/mauth-client-python)\n\nMAuth Client Python is an authentication library to manage the information needed to both sign and authenticate requests and responses for Medidata\'s MAuth authentication system.\n\n\n## Pre-requisites\n\nTo use MAuth Authenticator you will need:\n\n* An MAuth app ID\n* An MAuth private key (with the public key registered with Medidata\'s MAuth server)\n\n\n## Installation\n\nTo resolve packages using pip, add the following to ~/.pip/pip.conf:\n```\n[global]\nindex-url = https://<username>:<password>@mdsol.jfrog.io/mdsol/api/pypi/pypi-packages/simple/\n```\n\nInstall using pip:\n```\n$ pip install mauth-client\n```\n\nOr directly from GitHub:\n```\n$ pip install git+https://github.com/mdsol/mauth-client-python.git\n```\n\nThis will also install the dependencies.\n\nTo resolve using a requirements file, the index URL can be specified in the first line of the file:\n```\n--index-url https://<username>:<password>@mdsol.jfrog.io/mdsol/api/pypi/pypi-packages/simple/\nmauth-client==<latest version>\n```\n\n## Usage\n\n### Signing Outgoing Requests\n\n```python\nimport requests\nfrom mauth_client.requests_mauth import MAuth\n\n# MAuth configuration\nAPP_UUID = "<MAUTH_APP_UUID>"\nprivate_key = open("private.key", "r").read()\nmauth = MAuth(APP_UUID, private_key)\n\n# Call an MAuth protected resource, in this case an iMedidata API\n# listing the studies for a particular user\nuser_uuid = "10ac3b0e-9fe2-11df-a531-12313900d531"\nurl = "https://innovate.imedidata.com/api/v2/users/{}/studies.json".format(user_uuid)\n\n# Make the requests call, passing the auth client\nresult = requests.get(url, auth=mauth)\n\n# Print results\nif result.status_code == 200:\n    print([r["uuid"] for r in result.json()["studies"]])\nprint(result.text)\n```\n\nThe `mauth_sign_versions` option can be set as an environment variable to specify protocol versions to sign outgoing requests:\n\n| Key                   | Value                                                                                |\n| --------------------- | ------------------------------------------------------------------------------------ |\n| `MAUTH_SIGN_VERSIONS` | **(optional)** Comma-separated protocol versions to sign requests. Defaults to `v1`. |\n\nThis option can also be passed to the constructor:\n\n```python\nmauth_sign_versions = "v1,v2"\nmauth = MAuth(APP_UUID, private_key, mauth_sign_versions)\n```\n\n\n### Authenticating Incoming Requests\n\nMAuth Client Python supports AWS Lambda functions and Flask applications to authenticate MAuth signed requests.\n\nThe following variables are **required** to be configured in the environment variables:\n\n| Key            | Value                                                         |\n| -------------- | ------------------------------------------------------------- |\n| `APP_UUID`     | APP_UUID for the AWS Lambda function                          |\n| `PRIVATE_KEY`  | Encrypted private key for the APP_UUID                        |\n| `MAUTH_URL`    | MAuth service URL (e.g. https://mauth-innovate.imedidata.com) |\n\n\nThe following variables can optionally be set in the environment variables:\n\n| Key                    | Value                                                                                     |\n| ---------------------- | ----------------------------------------------------------------------------------------- |\n| `MAUTH_API_VERSION`    | **(optional)** MAuth API version. Only `v1` exists as of this writing. Defaults to `v1`.  |\n| `MAUTH_MODE`           | **(optional)** Method to authenticate requests. `local` or `remote`. Defaults to `local`. |\n| `V2_ONLY_AUTHENTICATE` | **(optional)** Authenticate requests with only V2. Defaults to `False`.                   |\n\n\n#### AWS Lambda functions\n\n```python\nfrom mauth_client.lambda_authenticator import LambdaAuthenticator\n\nauthenticator = LambdaAuthenticator(method, url, headers, body)\nauthentic, status_code, message = authenticator.is_authentic()\napp_uuid = authenticator.get_app_uuid()\n```\n\n#### Flask applications\n\nYou will need to create an application instance and initialize it with FlaskAuthenticator:\n\n```python\nfrom flask import Flask\nfrom mauth_client.flask_authenticator import FlaskAuthenticator\n\napp = Flask("Some Sample App")\nauthenticator = FlaskAuthenticator()\nauthenticator.init_app(app)\n```\n\nTo specify routes that need to be authenticated use the `requires_authentication` decorator:\n\n```python\nfrom flask import Flask\nfrom mauth_client.flask_authenticator import requires_authentication\n\n@app.route("/some/private/route", methods=["GET"])\n@requires_authentication\ndef private_route():\n    return "Wibble"\n\n@app.route("/app_status", methods=["GET"])\ndef app_status():\n    return "OK"\n```\n\n\n## Contributing\n\nSee [CONTRIBUTING](CONTRIBUTING.md)\n',
    'author': 'Medidata Solutions',
    'author_email': 'support@mdsol.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/mdsol/mauth-client-python',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
