# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['minicons']

package_data = \
{'': ['*']}

install_requires = \
['matplotlib>=3.4.1,<4.0.0',
 'polyleven>=0.7,<0.8',
 'torch>=1.8.0,<2.0.0',
 'transformers>=4.4.1,<5.0.0']

setup_kwargs = {
    'name': 'minicons',
    'version': '0.1.9',
    'description': 'A package of useful functions to analyze transformer based language models.',
    'long_description': '# minicons\n\n[![Downloads](https://static.pepy.tech/personalized-badge/minicons?period=total&units=international_system&left_color=black&right_color=brightgreen&left_text=Downloads)](https://pepy.tech/project/minicons)\n\nHelper functions for analyzing Transformer based representations of language\n\nThis repo is a wrapper around the `transformers` [library](https://huggingface.co/transformers) from hugging face :hugs:\n\n\n## Installation\n\nInstall from Pypi using:\n\n```pip install minicons```\n\n## Supported Functionality\n\n- Extract word representations from Contextualized Word Embeddings\n- Score sequences using language model scoring techniques, including masked language models following [Salazar et al. (2020)](https://www.aclweb.org/anthology/2020.acl-main.240.pdf).\n\n\n## Examples\n\n1. Extract word representations from contextualized word embeddings:\n\n```py\nfrom minicons import cwe\n\nmodel = cwe.CWE(\'bert-base-uncased\')\n\ncontext_words = [("I went to the bank to withdraw money.", "bank"), \n                 ("i was at the bank of the river ganga!", "bank")]\n\nprint(model.extract_representation(context_words, layer = 12))\n\n\'\'\' \ntensor([[ 0.5399, -0.2461, -0.0968,  ..., -0.4670, -0.5312, -0.0549],\n        [-0.8258, -0.4308,  0.2744,  ..., -0.5987, -0.6984,  0.2087]],\n       grad_fn=<MeanBackward1>)\n\'\'\'\n```\n\n2. Compute sentence acceptability measures (surprisals) using Incremental and Masked Language Models:\n\n```py\nfrom minicons import scorer\n\nmlm_model = scorer.MaskedLMScorer(\'bert-base-uncased\', \'cpu\')\nilm_model = scorer.IncrementalLMScorer(\'distilgpt2\', \'cpu\')\n\nstimuli = ["The keys to the cabinet are on the table.",\n           "The keys to the cabinet is on the table."]\n\nprint(mlm_model.score(stimuli, pool = torch.sum))\n\n\'\'\'\n[13.962650299072266, 23.41507911682129]\n\'\'\'\n\nprint(ilm_model.score(stimuli, pool = torch.sum))\n\n\'\'\'\n[41.51601982116699, 44.497480392456055]\n\'\'\'\n```\n\n## Tutorials\n\n- [Introduction to using LM-scoring methods using minicons](https://kanishka.xyz/post/minicons-running-large-scale-behavioral-analyses-on-transformer-lms/)\n- [Computing Surprisals using minicons](examples/surprisals.md)\n\n## Upcoming features:\n\n- Explore attention distributions extracted from transformers.\n- Contextual cosine similarities, i.e., compute a word\'s cosine similarity with every other word in the input context with batched computation.\n- Open to suggestions!\n',
    'author': 'Kanishka Misra',
    'author_email': 'kmisra@purdue.edu',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/kanishkamisra/minicons',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7',
}


setup(**setup_kwargs)
