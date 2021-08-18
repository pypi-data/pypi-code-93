# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fastapi_sso', 'fastapi_sso.sso']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.7.4',
 'fastapi<1',
 'oauthlib>=3.1.0',
 'pydantic>=1.8.1',
 'starlette>=0.13.6']

setup_kwargs = {
    'name': 'fastapi-sso',
    'version': '0.2.8',
    'description': 'FastAPI plugin to enable SSO to most common providers (such as Facebook login, Google login and login via Microsoft Office 365 Account)',
    'long_description': '# FastAPI SSO\n\nFastAPI plugin to enable SSO to most common providers (such as Facebook login, Google login and login via Microsoft Office 365 account).\n\nThis allows you to implement the famous `Login with Google/Facebook/Microsoft` buttons functionality on your backend very easily.\n\n## Installation\n\n### Install using `pip`\n\n```console\npip install fastapi-sso\n```\n\n### Install using `poetry`\n\n```console\npoetry add fastapi-sso\n```\n\n## Example\n\n### `example.py`\n\n```python\n"""This is an example usage of fastapi-sso.\n"""\n\nfrom fastapi import FastAPI\nfrom starlette.requests import Request\nfrom fastapi_sso.sso.google import GoogleSSO\n\napp = FastAPI()\n\ngoogle_sso = GoogleSSO("my-client-id", "my-client-secret", "https://my.awesome-web.com/google/callback")\n\n\n@app.get("/google/login")\nasync def google_login():\n    """Generate login url and redirect"""\n    return await google_sso.get_login_redirect()\n\n\n@app.get("/google/callback")\nasync def google_callback(request: Request):\n    """Process login response from Google and return user info"""\n    user = await google_sso.verify_and_process(request)\n    return {\n        "id": user.id,\n        "picture": user.picture,\n        "display_name": user.display_name,\n        "email": user.email,\n        "provider": user.provider,\n    }\n```\n\nRun using `uvicorn example:app`.\n',
    'author': 'Tomas Votava',
    'author_email': 'info@tomasvotava.eu',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://tomasvotava.github.io/fastapi-sso/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
