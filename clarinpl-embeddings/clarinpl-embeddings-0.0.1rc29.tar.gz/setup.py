# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['embeddings',
 'embeddings.data',
 'embeddings.embedding',
 'embeddings.embedding.static',
 'embeddings.evaluator',
 'embeddings.metric',
 'embeddings.model',
 'embeddings.pipeline',
 'embeddings.task',
 'embeddings.task.flair_task',
 'embeddings.transformation',
 'embeddings.transformation.flair_transformation',
 'embeddings.utils',
 'experimental',
 'experimental.datasets',
 'experimental.datasets.utils',
 'experimental.embeddings',
 'experimental.embeddings.language_models',
 'experimental.embeddings.scripts']

package_data = \
{'': ['*']}

install_requires = \
['Pillow==8.2.0',
 'datasets==1.6.1',
 'flair==0.8.0',
 'numpy==1.19.5',
 'requests==2.25.1',
 'scikit-learn==0.24.1',
 'seqeval==1.2.2',
 'spacy==3.1.0',
 'srsly==2.4.1',
 'tensorboard==2.4.1',
 'torch==1.9.0',
 'transformers==4.8.2',
 'typer==0.3.2']

setup_kwargs = {
    'name': 'clarinpl-embeddings',
    'version': '0.0.1rc29',
    'description': '',
    'long_description': None,
    'author': 'Roman Bartusiak',
    'author_email': 'riomus@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/CLARIN-PL/embeddings',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '==3.9.6',
}


setup(**setup_kwargs)
