# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nucleus']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.7.4,<4.0.0',
 'nest-asyncio>=1.5.1,<2.0.0',
 'requests>=2.23.0,<3.0.0',
 'tqdm>=4.41.0,<5.0.0']

extras_require = \
{':python_version >= "3.6.1" and python_version < "3.7"': ['dataclasses>=0.7,<0.8']}

setup_kwargs = {
    'name': 'scale-nucleus',
    'version': '0.1.17',
    'description': 'The official Python client library for Nucleus, the Data Platform for AI',
    'long_description': '# Nucleus\n\nhttps://dashboard.scale.com/nucleus\n\nAggregate metrics in ML are not good enough. To improve production ML, you need to understand their qualitative failure modes, fix them by gathering more data, and curate diverse scenarios.\n\nScale Nucleus helps you:\n\n- Visualize your data\n- Curate interesting slices within your dataset\n- Review and manage annotations\n- Measure and debug your model performance\n\nNucleus is a new way—the right way—to develop ML models, helping us move away from the concept of one dataset and towards a paradigm of collections of scenarios.\n\n## Installation\n\n`$ pip install scale-nucleus`\n\n## Common issues/FAQ\n\n### Outdated Client\n\nNucleus is iterating rapidly and as a result we do not always perfectly preserve backwards compatibility with older versions of the client. If you run into any unexpected error, it\'s a good idea to upgrade your version of the client by running\n```\npip install --upgrade scale-nucleus\n```\n\n## Usage\n\nFor the most up to date documentation, reference: https://dashboard.scale.com/nucleus/docs/api?language=python.\n\n## For Developers\n\nClone from github and install as editable\n\n```\ngit clone git@github.com:scaleapi/nucleus-python-client.git\ncd nucleus-python-client\npip3 install poetry\npoetry install\n```\n\nPlease install the pre-commit hooks by running the following command:\n\n```python\npoetry run pre-commit install\n```\n\n**Best practices for testing:**\n(1). Please run pytest from the root directory of the repo, i.e.\n\n```\npoetry run pytest tests/test_dataset.py\n```\n\n(2) To skip slow integration tests that have to wait for an async job to start.\n\n```\npoetry run pytest -m "not integration"\n```\n',
    'author': 'Scale AI Nucleus Team',
    'author_email': 'nucleusapi@scaleapi.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://scale.com/nucleus',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.6.2,<4.0.0',
}


setup(**setup_kwargs)
