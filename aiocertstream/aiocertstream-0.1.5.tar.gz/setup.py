# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['aiocertstream']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.7.4,<4.0.0']

setup_kwargs = {
    'name': 'aiocertstream',
    'version': '0.1.5',
    'description': 'An async client for certstream.',
    'long_description': '# aiocertstream\n\nAn async client to connect to certstream in Python.\n\n## Installation\n\n- Windows: `pip install aiocertstream` or `py -3 -m pip install aiocertstream`\n- *Nix: `pip3 install aiocertstream`\n\n## Example usage\n\nFor this example we\'ll just print out the cert index:\n\n```py\nfrom aiocertstream import Client\n\n\nclient = Client()\n\n@client.listen\nasync def my_handler(event: dict) -> None:\n    print(event["data"]["cert_index"])\n\nclient.run()\n```\n',
    'author': 'vcokltfre',
    'author_email': 'vcokltfre@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/vcokltfre/aiocertstream',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
