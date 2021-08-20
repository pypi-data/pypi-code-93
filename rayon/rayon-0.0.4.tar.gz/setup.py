# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['rayon', 'rayon.bin']

package_data = \
{'': ['*'],
 'rayon': ['etc/*',
           'etc/conf.d/*',
           'etc/nginx/*',
           'etc/rc.d/*',
           'static/*',
           'static/css/*',
           'static/js/*',
           'templates/*',
           'test/*',
           'user_conf/*',
           'var/html/*']}

install_requires = \
['Flask_RQ2[cli]',
 'XlsxWriter>=3.0.1,<4.0.0',
 'colorama',
 'gunicorn',
 'healthcheck',
 'matplotlib>=3.4.3,<4.0.0',
 'networkx>=2.6.2,<3.0.0',
 'pandas>=1.3.2,<2.0.0',
 'pony>=0.7.14,<0.8.0',
 'prometheus_client',
 'raven[flask]',
 'rq-dashboard',
 'scikit-learn>=0.24.2,<0.25.0',
 'sh',
 'superlance',
 'supervisor',
 'supervisor-wildcards',
 'xgboost>=1.4.2,<2.0.0',
 'xlrd>=2.0.1,<3.0.0']

entry_points = \
{'console_scripts': ['rayon = rayon.__main__:cli']}

setup_kwargs = {
    'name': 'rayon',
    'version': '0.0.4',
    'description': 'Web service for ProteinGraphML',
    'long_description': '.. epigraph:: I am the Lorax.  I speak for the trees.\n              --Dr. Seuss\n\n\nlorax implements a queued web service for calculating phylogenetic trees for\ngene families.  Lorax uses `HMMER`_ to do multiple sequence alignments,\n`FastTree`_ or `RAxML`_ to calculate trees,\n`RQ`_ to queue calculations, and `Flask`_ to serve up results.\n\n\n+-------------------+------------+------------+\n| Latest Release    | |pypi|     | |TheLorax| |\n+-------------------+------------+            +\n| GitHub            | |repo|     |            |\n+-------------------+------------+            +\n| License           | |license|  |            |\n+-------------------+------------+            +\n| Documentation     | |rtd|      |            |\n+-------------------+------------+            +\n| Travis Build      | |travis|   |            |\n+-------------------+------------+            +\n| Coverage          | |coverage| |            |\n+-------------------+------------+            +\n| Pythonicity       | |landscape||            |\n+-------------------+------------+            +\n| Code Grade        | |codacy|   |            |\n+-------------------+------------+            +\n| Dependencies      | |pyup|     |            |\n+-------------------+------------+            +\n| Working On        | |waffle|   |            |\n+-------------------+------------+            +\n| Issues            | |issues|   |            |\n+-------------------+------------+------------+\n\n\n.. |TheLorax| image:: docs/lorax_big_icon.jpg\n     :target: https://en.wikipedia.org/wiki/The_Lorax\n     :alt: Dr. Suess, The Lorax\n\n.. |pypi| image:: https://img.shields.io/pypi/v/lorax.svg\n    :target: https://pypi.python.org/pypi/lorax\n    :alt: Python package\n\n.. |repo| image:: https://img.shields.io/github/commits-since/LegumeFederation/lorax/0.94.svg\n    :target: https://github.com/LegumeFederation/lorax\n    :alt: GitHub repository\n\n.. |license| image:: https://img.shields.io/badge/License-BSD%203--Clause-blue.svg\n    :target: https://github.com/LegumeFederation/lorax/blob/master/LICENSE.txt\n    :alt: License terms\n\n.. |rtd| image:: https://readthedocs.org/projects/lorax/badge/?version=latest\n    :target: http://lorax.readthedocs.io/en/latest/?badge=latest\n    :alt: Documentation Status\n\n.. |travis| image:: https://img.shields.io/travis/LegumeFederation/lorax.svg\n    :target:  https://travis-ci.org/LegumeFederation/lorax\n    :alt: Travis CI\n\n.. |landscape| image:: https://landscape.io/github/LegumeFederation/lorax/master/landscape.svg?style=flat\n    :target: https://landscape.io/github/LegumeFederation/lorax\n    :alt: landscape.io status\n\n.. |codacy| image:: https://api.codacy.com/project/badge/Grade/2ebc65ca90f74dc7a9238c202f327981\n    :target: https://www.codacy.com/app/joelb123/lorax?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=LegumeFederation/lorax&amp;utm_campaign=Badge_Grade\n    :alt: Codacy.io grade\n\n.. |coverage| image:: https://codecov.io/gh/LegumeFederation/lorax/branch/master/graph/badge.svg\n    :target: https://codecov.io/gh/LegumeFederation/lorax\n    :alt: Codecov.io test coverage\n\n.. |issues| image:: https://img.shields.io/github/issues/LegumeFederation/lorax.svg\n    :target:  https://github.com/LegumeFederation/lorax/issues\n    :alt: Issues reported\n\n.. |requires| image:: https://requires.io/github/LegumeFederation/lorax/requirements.svg?branch=master\n     :target: https://requires.io/github/LegumeFederation/lorax/requirements/?branch=master\n     :alt: Requirements Status\n\n.. |pyup| image:: https://pyup.io/repos/github/LegumeFederation/lorax/shield.svg\n     :target: https://pyup.io/repos/github/LegumeFederation/lorax/\n     :alt: pyup.io dependencies\n\n.. |waffle| image:: https://badge.waffle.io/LegumeFederation/lorax.png?label=ready&title=Ready\n    :target: https://waffle.io/LegumeFederation/lorax\n    :alt: waffle.io status\n\n.. _Flask: http://flask.pocoo.org/\n.. _RQ: https://github.com/nvie/rq\n.. _HMMER: http://hmmer.org\n.. _RAxML: https://github.com/stamatak/standard-RAxML\n.. _FastTree: http://www.microbesonline.org/fasttree\n',
    'author': 'UNM Translational Informatics',
    'author_email': 'datascience.software@salud.unm.edu',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/unmtransinfo/rayon',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8.1,<3.10',
}


setup(**setup_kwargs)
