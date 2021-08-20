# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['cltk',
 'cltk.alphabet',
 'cltk.alphabet.grc',
 'cltk.core',
 'cltk.corpora',
 'cltk.corpora.grc',
 'cltk.corpora.grc.tlg',
 'cltk.corpora.lat',
 'cltk.corpora.lat.phi',
 'cltk.data',
 'cltk.dependency',
 'cltk.embeddings',
 'cltk.languages',
 'cltk.lemmatize',
 'cltk.lexicon',
 'cltk.morphology',
 'cltk.ner',
 'cltk.phonology',
 'cltk.phonology.ang',
 'cltk.phonology.arb',
 'cltk.phonology.arb.utils',
 'cltk.phonology.arb.utils.pyarabic',
 'cltk.phonology.enm',
 'cltk.phonology.gmh',
 'cltk.phonology.got',
 'cltk.phonology.grc',
 'cltk.phonology.lat',
 'cltk.phonology.non',
 'cltk.phonology.non.old_swedish',
 'cltk.prosody',
 'cltk.prosody.lat',
 'cltk.sentence',
 'cltk.stem',
 'cltk.stops',
 'cltk.tag',
 'cltk.text',
 'cltk.tokenizers',
 'cltk.tokenizers.lat',
 'cltk.utils',
 'cltk.wordnet']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=5.4.1,<6.0.0',
 'boltons>=20.0.0,<21.0.0',
 'fasttext>=0.9.1,<0.10.0',
 'gensim>=3.8.1,<4.0.0',
 'gitpython>=3.0,<4.0',
 'greek-accentuation>=1.2.0,<2.0.0',
 'nltk>=3.5,<4.0',
 'python-Levenshtein>=0.12.0,<0.13.0',
 'requests>=2.22.0,<3.0.0',
 'scikit-learn>=0.24.2,<0.25.0',
 'spacy>=2.3.5,<3.0.0',
 'stanza==1.1.1',
 'stringcase>=1.2,<2.0',
 'tqdm>=4.41.1,<5.0.0']

setup_kwargs = {
    'name': 'cltk',
    'version': '1.0.18',
    'description': 'The Classical Language Toolkit',
    'long_description': "|travis| |pypi| |zenodo|\n\n\n.. |travis| image:: https://travis-ci.org/cltk/cltk.svg?branch=master\n   :target: https://travis-ci.org/cltk/cltk\n\n.. |rtd| image:: https://img.shields.io/readthedocs/cltk\n   :target: http://docs.cltk.org/\n\n.. |codecov| image:: https://codecov.io/gh/cltk/cltk/branch/master/graph/badge.svg\n   :target: https://codecov.io/gh/cltk/cltk\n\n.. |pypi| image:: https://img.shields.io/pypi/v/cltk\n   :target: https://pypi.org/project/cltk/\n\n.. |zenodo| image:: https://zenodo.org/badge/DOI/10.5281/zenodo.3445585.svg\n   :target: https://doi.org/10.5281/zenodo.3445585\n\n.. |binder| image:: https://mybinder.org/badge_logo.svg\n   :target: https://mybinder.org/v2/gh/cltk/tutorials/master\n\n\nThe Classical Language Toolkit (CLTK) is a Python library offering natural language processing (NLP) for pre-modern languages.\n\n\nInstallation\n============\n\nFor the CLTK's latest version:\n\n.. code-block:: bash\n\n   $ pip install cltk\n\nFor more information, see `Installation docs <https://docs.cltk.org/en/latest/installation.html>`_ or, to install from source, `Development <https://docs.cltk.org/en/latest/development.html>`_.\n\nPre-1.0 software remains available on the `branch v0.1.x <https://github.com/cltk/cltk/tree/v0.1.x>`_ and docs at `<https://legacy.cltk.org>`_.\n\n\nDocumentation\n=============\n\nDocumentation at `<https://docs.cltk.org>`_.\n\n\nCitation\n========\n\n.. code-block:: bibtex\n\n   @Misc{johnsonetal2014,\n    author = {Johnson, Kyle P. and Patrick Burns and John Stewart and Todd Cook and Clément Besnier and William J. B. Mattingly},\n    title = {CLTK: The Classical Language Toolkit},\n    url = {https://github.com/cltk/cltk},\n    year = {2014--2021},\n   }\n\n\nLicense\n=======\n\n.. |year| date:: %Y\n\nCopyright (c) 2014-|year| Kyle P. Johnson under the `MIT License <https://github.com/cltk/cltk/blob/master/LICENSE>`_.\n",
    'author': 'Kyle P. Johnson',
    'author_email': 'kyle@kyle-p-johnson.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'http://cltk.org',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
