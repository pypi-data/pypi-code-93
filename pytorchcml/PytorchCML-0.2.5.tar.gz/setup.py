# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['PytorchCML',
 'PytorchCML.evaluators',
 'PytorchCML.losses',
 'PytorchCML.models',
 'PytorchCML.regularizers',
 'PytorchCML.samplers',
 'PytorchCML.trainers']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.19.5,<2.0.0',
 'pandas>=1.1.5,<2.0.0',
 'scikit-learn>=0.22.2,<0.23.0',
 'scipy>=1.4.1,<2.0.0',
 'torch>=1.8.1,<2.0.0',
 'tqdm>=4.41.1,<5.0.0']

setup_kwargs = {
    'name': 'pytorchcml',
    'version': '0.2.5',
    'description': 'Collaborative Metric Learning implemented by Pytorch',
    'long_description': '# Pytorch CML\nCollaborative Metric Learning implemented by pytorch\n\n# Usage\n1. Set model, optimizer, loss, sampler and evaluator.\n2. Input these to trainer.\n3. Run fit method.\n\nSee examples for detail.',
    'author': 'hand10ryo',
    'author_email': 'hand10ryo@yahoo.co.jp',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/hand10ryo/PytorchCML',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.10,<3.10',
}


setup(**setup_kwargs)
