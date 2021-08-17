# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fastapi_azure_auth']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.7.4,<4.0.0',
 'fastapi>=0.68.0,<0.69.0',
 'python-jose[cryptography]>=3.3.0,<4.0.0']

setup_kwargs = {
    'name': 'fastapi-azure-auth',
    'version': '1.1.1',
    'description': 'Easy and secure implementation of Azure AD for your FastAPI APIs',
    'long_description': '<h1 align="center">\n  <img src=".github/images/intility.png" width="124px"/><br/>\n  FastAPI-Azure-auth\n</h1>\n\n<p align="center">\n    <em>Azure AD Authentication for FastAPI apps made easy.</em>\n</p>\n<p align="center">\n    <a href="https://python.org">\n        <img src="https://img.shields.io/badge/python-v3.9+-blue.svg?logo=python&logoColor=white&label=python" alt="Python version">\n    </a>\n    <a href="https://fastapi.tiangolo.com/">\n        <img src="https://img.shields.io/badge/FastAPI-0.68.0+%20-blue.svg?logo=fastapi&logoColor=white&label=fastapi" alt="FastAPI Version">\n    </a>\n    <a href="https://pypi.org/pypi/fastapi-azure-auth">\n        <img src="https://img.shields.io/pypi/v/fastapi-azure-auth.svg?logo=pypi&logoColor=white&label=pypi" alt="Package version">\n    </a>\n</p>\n<p align="center">\n    <a href="https://codecov.io/gh/intility/fastapi-azure-auth">\n        <img src="https://codecov.io/gh/intility/fastapi-azure-auth/branch/main/graph/badge.svg?token=BTFGII4GYR" alt="Codecov">\n    </a>\n    <a href="https://github.com/pre-commit/pre-commit">\n        <img src="https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white" alt="Pre-commit">\n    </a>\n    <a href="https://github.com/psf/black">\n        <img src="https://img.shields.io/badge/code%20style-black-000000.svg" alt="Black">\n    </a>\n    <a href="http://mypy-lang.org">\n        <img src="http://www.mypy-lang.org/static/mypy_badge.svg" alt="mypy">\n    </a>\n    <a href="https://pycqa.github.io/isort/">\n        <img src="https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336" alt="isort">\n    </a>\n</p>\n\n\n## 🚀 Description\n\n> FastAPI is a modern, fast (high-performance), web framework for building APIs with Python, based on standard Python type hints.  \n  \nAt Intility, FastAPI is a popular framework among its developers, \nwith customer-facing and internal services developed entirely on a FastAPI backend.\n\nThis package enables our developers (and you 😊) to create features without worrying about authentication and authorization.  \n\nAlso, [we\'re hiring!](https://intility.no/en/career/)\n\n## ⚡️ Quick start\n### Azure\nAzure docs will be available when create-fastapi-app is developed. In the meantime \nplease use the [.NET](https://create.intility.app/dotnet/setup/authorization) documentation.\n\n\n### FastAPI\n\n1. Install this library:\n```bash\npip install fastapi-azure-auth\n# or\npoetry add fastapi-azure-auth\n```\n\n2. Include `swagger_ui_oauth2_redirect_url` and `swagger_ui_init_oauth` in your FastAPI app initialization:\n\n```python\napp = FastAPI(\n    ...\n    swagger_ui_oauth2_redirect_url=\'/oauth2-redirect\',\n    swagger_ui_init_oauth={\n        \'usePkceWithAuthorizationCodeGrant\': True, \n        \'clientId\': settings.OPENAPI_CLIENT_ID  # SPA app with grants to your app\n    },\n)\n```\n\n3. Ensure you have CORS enabled for your local environment, such as `http://localhost:8000`. See [main.py](main.py) \nand the `BACKEND_CORS_ORIGINS` in [config.py](demoproj/core/config.py) \n\n4. Import and configure your Azure authentication:\n\n```python\nfrom fastapi_azure_auth.auth import AzureAuthorizationCodeBearer\n\nazure_scheme = AzureAuthorizationCodeBearer(\n    app=app,\n    app_client_id=settings.APP_CLIENT_ID,  # Web app\n    scopes={\n        f\'api://{settings.APP_CLIENT_ID}/user_impersonation\': \'User Impersonation\',\n    },\n)\n```\n\n5. Set your `intility_scheme` as a dependency for your wanted views/routers:\n\n```python\napp.include_router(api_router, prefix=settings.API_V1_STR, dependencies=[Depends(azure_scheme)])\n```\n\n## ⚙️ Configuration\nFor those using a non-Intility tenant, you also need to make changes to the `provider_config`:\n\n```python\nfrom fastapi_azure_auth.provider_config import provider_config\n\nintility_scheme = AzureAuthorizationCodeBearer(\n    ...\n)\n\nprovider_config.tenant_id = \'my-own-tenant-id\'\n```\n\n\nIf you want, you can deny guest users to access your API by passing the `allow_guest_users=False`\nto `AzureAuthorizationCodeBearer`:\n\n```python\nintility_scheme = AzureAuthorizationCodeBearer(\n    ...\n    allow_guest_users=False\n)\n```\n\n## 💡 Nice to knows\n\nA `User` object is attached to the request state if the token is valid. Unparsed claims can be accessed at\n`request.state.user.claims`.\n\n```python\nfrom fastapi_azure_auth.user import User\nfrom fastapi import Request\n\n@router.get(...)\nasync def world(request: Request) -> dict:\n    user: User = request.state.user\n    return {\'user\': user}\n```',
    'author': 'Jonas Krüger Svensson',
    'author_email': 'jonas.svensson@intility.no',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/intility/fastapi-azure-auth',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
