# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['poe_client', 'poe_client.schemas']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.7.4,<4.0.0',
 'black>=21.7b0,<22.0',
 'pydantic>=1.8.2,<2.0.0',
 'pyhumps>=3.0.2,<4.0.0',
 'pytest-asyncio>=0.15.1,<0.16.0']

setup_kwargs = {
    'name': 'poe-client',
    'version': '0.3.1',
    'description': 'Async PoE API client with rate limit support (upcoming)',
    'long_description': '# poe-client\n\n[![Build Status](https://github.com/BPL-Development-Team/poe-client/workflows/test/badge.svg?branch=master&event=push)](https://github.com/BPL-Development-Team/poe-client/actions?query=workflow%3Atest)\n[![codecov](https://codecov.io/gh/BPL-Development-Team/poe-client/branch/master/graph/badge.svg)](https://codecov.io/gh/BPL-Development-Team/poe-client)\n[![Python Version](https://img.shields.io/pypi/pyversions/poe-client.svg)](https://pypi.org/project/poe-client/)\n[![wemake-python-styleguide](https://img.shields.io/badge/style-wemake-000000.svg)](https://github.com/wemake-services/wemake-python-styleguide)\n\nAsync PoE API client with rate limit support.\n\n## WARNING\nThis project is in an pre-alpha stage and has not been tested properly in production. Use with caution.\n\n## Features\n\n- Asynchronous HTTP client based on aiohttp\n- Up-to-date with all PoE API endpoints\n- All PoE API types defined as Pydantic schemas (Can generate OpenAPI Specifications)\n- 100% test coverage and style enforced with wemake\'s flake8\n- Fully typed with pydantic and checked with mypy, [PEP561 compatible](https://www.python.org/dev/peps/pep-0561/)\n\n\n## Limitations\nThere is no API endpoint only to fetch rate limit headers. This means that the Client is not aware of what rules exist until it makes a real request.\nThus, be aware that sending too many request at the same time leads to being rate limited. Try to batch by 5, we\'ve seen this as a safe level of concurrency.\n\n## Installation\n\n```bash\npip install poe-client\n```\n\n\n## Example\n\nShowcase how your project can be used:\n\n```python\nfrom typing import List\nimport os\n\nfrom poe_client.client import Client, PoEClient\nfrom poe_client.schemas.league import League\n\ntoken = os.environ["POE_TOKEN"]\ncontact = os.environ["POE_CONTACT"]\n\nif not token or not contact:\n    raise EnvironmentError("Need to set both POE_TOKEN and POE_CONTACT")\n\n\nclient = PoEClient(\n    token,\n    "poe-client",\n    "1.0",\n    contact,\n)\n\nasync def list_leagues():\n    """List leagues."""\n    leagues: List[League] = []\n    async with client:\n        leagues = await client.list_leagues()\n\n    logging.info(leagues)\n```\n\n## License\n\n[MIT](https://github.com/BPL-Development-Team/poe-client/blob/master/LICENSE)\n\n\n## Credits\n\nThis project was generated with [`wemake-python-package`](https://github.com/wemake-services/wemake-python-package). Current template version is: [6cb0736bbc9cb53ee126e2297b8ed7029b5e1380](https://github.com/wemake-services/wemake-python-package/tree/6cb0736bbc9cb53ee126e2297b8ed7029b5e1380). See what is [updated](https://github.com/wemake-services/wemake-python-package/compare/6cb0736bbc9cb53ee126e2297b8ed7029b5e1380...master) since then.\n',
    'author': 'bittermandel',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/BPL-Development-Team/poe-client',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6.2,<4.0.0',
}


setup(**setup_kwargs)
