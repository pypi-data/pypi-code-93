# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['pspca']

package_data = \
{'': ['*']}

install_requires = \
['matplotlib>=3.4.3,<4.0.0', 'numpy>=1.21.2,<2.0.0']

setup_kwargs = {
    'name': 'pspca',
    'version': '0.0.1a0',
    'description': 'Prjective Space PCA',
    'long_description': "Prjective Space PCA\n===================\n\n|PyPI| |Status| |Python Version| |License|\n\n|Read the Docs| |Tests| |Codecov|\n\n|pre-commit| |Black|\n\n.. |PyPI| image:: https://img.shields.io/pypi/v/pspca.svg\n   :target: https://pypi.org/project/pspca/\n   :alt: PyPI\n.. |Status| image:: https://img.shields.io/pypi/status/pspca.svg\n   :target: https://pypi.org/project/pspca/\n   :alt: Status\n.. |Python Version| image:: https://img.shields.io/pypi/pyversions/pspca\n   :target: https://pypi.org/project/pspca\n   :alt: Python Version\n.. |License| image:: https://img.shields.io/pypi/l/pspca\n   :target: https://opensource.org/licenses/MIT\n   :alt: License\n.. |Read the Docs| image:: https://img.shields.io/readthedocs/pspca/latest.svg?label=Read%20the%20Docs\n   :target: https://pspca.readthedocs.io/\n   :alt: Read the documentation at https://pspca.readthedocs.io/\n.. |Tests| image:: https://github.com/gatoniel/pspca/workflows/Tests/badge.svg\n   :target: https://github.com/gatoniel/pspca/actions?workflow=Tests\n   :alt: Tests\n.. |Codecov| image:: https://codecov.io/gh/gatoniel/pspca/branch/main/graph/badge.svg\n   :target: https://codecov.io/gh/gatoniel/pspca\n   :alt: Codecov\n.. |pre-commit| image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white\n   :target: https://github.com/pre-commit/pre-commit\n   :alt: pre-commit\n.. |Black| image:: https://img.shields.io/badge/code%20style-black-000000.svg\n   :target: https://github.com/psf/black\n   :alt: Black\n\n\nFeatures\n--------\n\n* TODO\n\n\nRequirements\n------------\n\n* TODO\n\n\nInstallation\n------------\n\nYou can install *Prjective Space PCA* via pip_ from PyPI_:\n\n.. code:: console\n\n   $ pip install pspca\n\n\nUsage\n-----\n\nPlease see the `Command-line Reference <Usage_>`_ for details.\n\n\nContributing\n------------\n\nContributions are very welcome.\nTo learn more, see the `Contributor Guide`_.\n\n\nLicense\n-------\n\nDistributed under the terms of the `MIT license`_,\n*Prjective Space PCA* is free and open source software.\n\n\nIssues\n------\n\nIf you encounter any problems,\nplease `file an issue`_ along with a detailed description.\n\n\nCredits\n-------\n\nThis project was generated from `@cjolowicz`_'s `Hypermodern Python Cookiecutter`_ template.\n\n.. _@cjolowicz: https://github.com/cjolowicz\n.. _Cookiecutter: https://github.com/audreyr/cookiecutter\n.. _MIT license: https://opensource.org/licenses/MIT\n.. _PyPI: https://pypi.org/\n.. _Hypermodern Python Cookiecutter: https://github.com/cjolowicz/cookiecutter-hypermodern-python\n.. _file an issue: https://github.com/gatoniel/pspca/issues\n.. _pip: https://pip.pypa.io/\n.. github-only\n.. _Contributor Guide: CONTRIBUTING.rst\n.. _Usage: https://pspca.readthedocs.io/en/latest/usage.html\n",
    'author': 'Niklas Netter',
    'author_email': 'niklas.netter@unibas.ch',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/gatoniel/pspca',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.1,<3.11',
}


setup(**setup_kwargs)
