# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['cutty',
 'cutty.compat',
 'cutty.entrypoints',
 'cutty.entrypoints.cli',
 'cutty.filestorage',
 'cutty.filestorage.adapters',
 'cutty.filestorage.adapters.observers',
 'cutty.filestorage.domain',
 'cutty.filesystems',
 'cutty.filesystems.adapters',
 'cutty.filesystems.domain',
 'cutty.repositories',
 'cutty.repositories.adapters',
 'cutty.repositories.adapters.fetchers',
 'cutty.repositories.adapters.providers',
 'cutty.repositories.domain',
 'cutty.services',
 'cutty.templates',
 'cutty.templates.adapters',
 'cutty.templates.adapters.cookiecutter',
 'cutty.templates.domain',
 'cutty.util']

package_data = \
{'': ['*']}

install_requires = \
['Jinja2>=2.11.3,<4.0.0',
 'binaryornot>=0.4.4,<0.5.0',
 'click>=8.0.1,<9.0.0',
 'httpx>=0.18.1,<0.19.0',
 'jinja2-time>=0.2.0,<0.3.0',
 'lazysequence>=0.2.1,<0.4.0',
 'platformdirs>=2.0.2,<3.0.0',
 'pluggy>=0.13.1,<0.14.0',
 'pygit2>=1.5.0,<2.0.0',
 'python-slugify>=5.0.0,<6.0.0',
 'yarl>=1.6.3,<2.0.0']

entry_points = \
{'console_scripts': ['cutty = cutty.__main__:main']}

setup_kwargs = {
    'name': 'cutty',
    'version': '0.10.0',
    'description': 'cutty',
    'long_description': "cutty\n=====\n\n|PyPI| |Status| |Python Version| |License| |Read the Docs| |Tests| |Codecov|\n\n.. |PyPI| image:: https://img.shields.io/pypi/v/cutty.svg\n   :target: https://pypi.org/project/cutty/\n   :alt: PyPI\n.. |Status| image:: https://img.shields.io/pypi/status/cutty.svg\n   :target: https://pypi.org/project/cutty/\n   :alt: Status\n.. |Python Version| image:: https://img.shields.io/pypi/pyversions/cutty\n   :target: https://pypi.org/project/cutty\n   :alt: Python Version\n.. |License| image:: https://img.shields.io/pypi/l/cutty\n   :target: https://opensource.org/licenses/MIT\n   :alt: License\n.. |Read the Docs| image:: https://img.shields.io/readthedocs/cutty/latest.svg?label=Read%20the%20Docs\n   :target: https://cutty.readthedocs.io/\n   :alt: Read the documentation at https://cutty.readthedocs.io/\n.. |Tests| image:: https://github.com/cjolowicz/cutty/workflows/Tests/badge.svg\n   :target: https://github.com/cjolowicz/cutty/actions?workflow=Tests\n   :alt: Tests\n.. |Codecov| image:: https://codecov.io/gh/cjolowicz/cutty/branch/main/graph/badge.svg\n   :target: https://codecov.io/gh/cjolowicz/cutty\n   :alt: Codecov\n\n\nAn experimental Cookiecutter clone :construction:\n\n\nRequirements\n------------\n\n* Python 3.9\n\n\nInstallation\n------------\n\nYou can install *cutty* via pip_ from PyPI_:\n\n.. code:: console\n\n   $ pip install cutty\n\n\nUsage\n-----\n\nPlease see the `Command-line Reference <Usage_>`_ for details.\n\n\nContributing\n------------\n\nContributions are very welcome.\nTo learn more, see the `Contributor Guide`_.\n\n\nLicense\n-------\n\nDistributed under the terms of the `MIT license`_,\n*cutty* is free and open source software.\n\n\nIssues\n------\n\nIf you encounter any problems,\nplease `file an issue`_ along with a detailed description.\n\n\nCredits\n-------\n\nThis project was generated from `@cjolowicz`_'s `Hypermodern Python Cookiecutter`_ template.\n\n.. _@cjolowicz: https://github.com/cjolowicz\n.. _Cookiecutter: https://github.com/audreyr/cookiecutter\n.. _MIT license: https://opensource.org/licenses/MIT\n.. _PyPI: https://pypi.org/\n.. _Hypermodern Python Cookiecutter: https://github.com/cjolowicz/cookiecutter-hypermodern-python\n.. _file an issue: https://github.com/cjolowicz/cutty/issues\n.. _pip: https://pip.pypa.io/\n.. github-only\n.. _Contributor Guide: CONTRIBUTING.rst\n.. _Usage: https://cutty.readthedocs.io/en/latest/usage.html\n",
    'author': 'Claudio Jolowicz',
    'author_email': 'mail@claudiojolowicz.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/cjolowicz/cutty',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
