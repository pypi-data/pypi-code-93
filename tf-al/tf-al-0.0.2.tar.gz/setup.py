# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['tf_al', 'tf_al.utils', 'tf_al.wrapper']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1,<2',
 'scikit-learn>=0.24.2,<0.25.0',
 'tensorflow>=2,<3',
 'tqdm>=4.62.2,<5.0.0']

setup_kwargs = {
    'name': 'tf-al',
    'version': '0.0.2',
    'description': 'Active learning with tensorflow. Create custom and generic active learning loops. Export and share your experiments.',
    'long_description': '\n# Active learning with tensorflow\n\n\n# Index\n\n1. [Installation](#Installation)\n2. [Getting started](#Getting-started)\n    1. [Model wrapper](#Model-wrapper)\n    2. [Acquisition functions](#Acquisition-functions)\n    1. [Basic active learning loop](#Basic-active-learning-loop)\n3. [Development](#Development)\n    1. [Setup](#Setup)\n    2. [Scripts](#Scripts)\n4. [Contribution](#Contribution)\n5. [Issues](#Issues)\n\n\n\n# Installation\n\n\n```shell\n$ pip install tf-al\n```\n\n\n# Getting started\n\nThe library \n\n\n## Model wrapper\n\nModel wrappers are use to create interfaces to the active learning loop.\n\n\n\n## Acquisition functions\n\n\n\n\n\n## Basic active learning loop\n\n\n```\nimport tensorflow as tf\nfrom tf_al import ActiveLearningLoop, Dataset, Pool\n\n\n\n```\n\n\n\n\n\n\n\n# Development\n\n## Setup\n\n1. Create a virtual env (optional)\n2. [Install and Setup Poetry](https://python-poetry.org/docs/#installation)\n3. Install package dependencies using poetry\n\n\n## Scripts\n\n### Create documentation\n\nTo create documentation for the `./active_leanring` directory. Execute following command\nin `./docs`\n\n```shell\n$ make html\n```\n\n### Run tests\n\nTo perform automated unittests run following command in the root package directory.\n\n```shell\n$ pytest\n```\n\nTo generate additional coverage reports run.\n\n```shell\n$ pytest --cov\n```\n\n\n\n# Contribution\n\n# Issues',
    'author': 'Maksim Sandybekov',
    'author_email': 'maksim.sandybekov@live.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ExLeonem/tf-al',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
