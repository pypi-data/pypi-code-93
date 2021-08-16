# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['scalewiz', 'scalewiz.components', 'scalewiz.helpers', 'scalewiz.models']

package_data = \
{'': ['*']}

install_requires = \
['appdirs>=1.4.4,<2.0.0',
 'matplotlib>=3.4.2,<4.0.0',
 'pandas>=1.2.2,<2.0.0',
 'py-hplc>=1.0.1,<2.0.0',
 'tkcalendar>=1.6.1,<2.0.0',
 'tomlkit>=0.7.0,<0.8.0']

entry_points = \
{'console_scripts': ['scalewiz = scalewiz.__main__:main']}

setup_kwargs = {
    'name': 'scalewiz',
    'version': '0.5.9',
    'description': 'A graphical user interface for chemical performance testing designed to work with Teledyne SSI MX-class HPLC pumps.',
    'long_description': '===========================================================================================\nscalewiz |license| |python| |pypi| |build-status| |style| |code quality| |maintainability|\n===========================================================================================\n\nA graphical user interface designed to work with `Teledyne SSI MX-class\nHPLC pumps`_ for the purpose of calcite scale inhibitor chemical\nperformance testing.\n\nIf you are working with Teledyne SSI Next Generation pumps generally, please check out `py-hplc`_!\n\nIf you notice something weird, fragile, or otherwise encounter a bug, please open an `issue`_.\n\n.. image:: https://raw.githubusercontent.com/teauxfu/scalewiz/main/img/main_menu.PNG\n\n.. image:: https://raw.githubusercontent.com/teauxfu/scalewiz/main/img/evaluation(plot).PNG\n\nInstallation\n============\n\n::\n\n    python -m pip install --user scalewiz\n\nOr, if you use :code:`pipx` (`try it!`_ 😉) ::\n\n    pipx install scalewiz\n\nUsage\n=====\n\n::\n\n    python -m scalewiz\n\nIf Python is on your PATH (or you used :code:`pipx` 😎), simply ::\n\n    scalewiz\n\n\nFurther instructions can be viewed in the `docs`_ section of this repo or with the Help button in the main\nmenu.\n\nAcknowledgements\n================\n- `Premier Chemical Technologies, LLC`_ for sponsoring development\n-  `@balacla`_ for support and invaluable help in brainstorming\n\n.. |license| image:: https://img.shields.io/github/license/teauxfu/scalewiz\n  :target: https://github.com/teauxfu/py-hplc/blob/main/COPYING\n  :alt: GitHub\n\n.. |python| image:: https://img.shields.io/pypi/pyversions/scalewiz\n  :alt: PyPI - Python Version\n\n.. |pypi| image:: https://img.shields.io/pypi/v/scalewiz\n  :target: https://pypi.org/project/scalewiz/\n  :alt: PyPI\n\n.. |build-status| image:: https://github.com/teauxfu/scalewiz/actions/workflows/build.yml/badge.svg\n  :target: https://github.com/teauxfu/scalewiz/actions/workflows/build.yml\n  :alt: Build Status\n\n.. |docs| image:: https://readthedocs.org/projects/pip/badge/?version=stable\n  :target: https://scalewiz.readthedocs.io/en/latest/\n  :alt: Documentation Status\n\n.. |style| image:: https://img.shields.io/badge/code%20style-black-000000.svg\n  :target: https://github.com/psf/black\n  :alt: Style\n\n.. |code quality| image:: https://img.shields.io/badge/code%20quality-flake8-black\n  :target: https://gitlab.com/pycqa/flake8\n  :alt: Code quality\n  \n.. |maintainability| image:: https://api.codeclimate.com/v1/badges/9f4d424afac626a8b2e3/maintainability\n   :target: https://codeclimate.com/github/teauxfu/scalewiz/maintainability\n   :alt: Maintainability\n\n\n.. _`Premier Chemical Technologies, LLC`: https://premierchemical.tech\n.. _`@balacla`: https://github.com/balacla\n.. _`Teledyne SSI MX-class HPLC pumps`: https://store.teledynessi.com/collections/mx-class\n.. _`py-hplc`: https://github.com/teauxfu/py-hplc\n.. _`docs`: https://github.com/teauxfu/scalewiz/blob/main/doc/index.rst#scalewiz-user-guide\n.. _`issue`: https://github.com/teauxfu/scalewiz/issues\n.. _`try it!`: https://pypa.github.io/pipx/\n',
    'author': 'Alex Whittington',
    'author_email': 'alex@southsun.tech',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
