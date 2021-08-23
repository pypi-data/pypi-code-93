# -*- coding: utf-8 -*-
from distutils.core import setup

package_dir = \
{'': 'src'}

packages = \
['igenius_adapters_sdk',
 'igenius_adapters_sdk.entities',
 'igenius_adapters_sdk.tools']

package_data = \
{'': ['*']}

install_requires = \
['pydantic>=1.7.2,<2.0.0', 'typing-extensions>=3.10.0,<4.0.0']

setup_kwargs = {
    'name': 'igenius-adapters-sdk',
    'version': '1.7.1',
    'description': 'The iGenius Software Development Kit to develop crystal datasource adapters.',
    'long_description': '# iGenius Adapters SDK\n\nThis is the Software Development Kit for iGenius Web Connectors development.  \nYou can use our SDK in your project to be able to handle correctly the data structures that will be used by iGenius services to call your web connector adapter.\nFurther information about SDK can be found in the [official documentation](https://webconnectors.crystal.ai/sdk/latest/), instead check [What is a Web Connector](https://webconnectors.crystal.ai/docs/latest/) to know more \nabout the data sharing with _Crystal_.\n\n## Installation\n\nWith Poetry\n\n```bash\npoetry add igenius-adapters-sdk\n```\n\nWith pip\n\n```bash\npip install igenius-adapters-sdk\n```\n\n## Releases\n\nSee the [CHANGELOG.md](/CHANGELOG.md) file.\n\n## License\n\nAll the content in this repository is licensed under the [Apache license, version 2.0](http://www.apache.org/licenses/LICENSE-2.0.txt). The full license text can be found in the [LICENSE](/LICENSE) file.',
    'author': 'iGenius Backend',
    'author_email': 'backend@igenius.ai',
    'url': 'https://github.com/iGenius-Srl/igenius-adapters-sdk',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
