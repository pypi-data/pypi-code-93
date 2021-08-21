# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['apav',
 'apav.analysis',
 'apav.core',
 'apav.qtwidgets',
 'apav.tests',
 'apav.utils',
 'apav.visualization']

package_data = \
{'': ['*'], 'apav': ['resources/icons/*', 'resources/testdata/*']}

install_requires = \
['PyQt5>=5.11',
 'fast-histogram',
 'lmfit>=1.0',
 'numba',
 'numpy>=1.17',
 'periodictable',
 'pyqtgraph>=0.11.0',
 'pytest-qt>=3',
 'pytest>=5',
 'tabulate']

setup_kwargs = {
    'name': 'apav',
    'version': '1.2.1',
    'description': 'A Python library for Atom Probe Tomography analysis',
    'long_description': '# APAV: Python analysis for atom probe tomography\n[![Documentation Status](https://readthedocs.org/projects/apav/badge/?version=latest)](https://apav.readthedocs.io/en/latest/?badge=latest)\n[![coverage report](https://gitlab.com/jesseds/apav/badges/master/coverage.svg)](https://gitlab.com/jesseds/apav/commits/master)\n[![pipeline status](https://gitlab.com/jesseds/apav/badges/master/pipeline.svg)](https://gitlab.com/jesseds/apav/-/commits/master)\n\nAPAV (Atom Probe Analysis and Visualization) is a Python library for the analysis and\nvisualization of atom probe tomography experiments.\n\n* Multiple event dependent mass or time-of-flight spectra\n* Correlation histograms\n* Molecular isotopic calculations\n* .pos, .epos, .ato files or synthetic data\n* Mass spectrum quantification with multiple fitting schemes\n* Interactive visualizations\n\nAPAV can perform a number of analyses common in field evaporation science, although it focuses\non analyses relating to detector multiple events. A "Multiple event" refers to a phenomenon where\nmultiple ions (elemental or molecular) strike the micro-channel plates between pulses.\n\nAPAV is open source (GPLv2_ or greater) and runs on Windows, Linux, Mac OS - or anything able to run a python\ninterpreter. It is written in Python 3 using NumPy to accelerate mathematical computations, and other math tools\nfor more niche calculations. Visualizations leverage pyqtgraph and other custom Qt widgets.\n\n# Support\nPost issues and questions to the [GitLab issue tracker](https://gitlab.com/jesseds/apav/-/issues)\n\n# Documentation\nDocumentation is found at: https://apav.readthedocs.io/\n\n# FAQ\n**Why use this over IVAS or program X?**\n\nAPAV was never intended to be used as an IVAS substitute or replacement. While much of the \nfunctionality may be similar/redundant, APAV fills feature gaps in IVAS found lacking (or simply non-existent).\nSpecifically:\n1. Multiple-event analysis (correlation histograms, multiple event histograms, multiple event mass quantifications.\n2. Full control over mass spectrum analysis (background models, fitting, binning).\n3. Provide an interface for developing custom analyses through common ePOS, POS, ATO, RNG, RRNG files.\n\n**Why is there no GUI for APAV?**\n\nAs APAV is a python *library*, there is no plan for a graphical user interface for APAV. It does, however, include\ncustom interactive visualization tools using pyqtgraph and custom Qt widgets (for various graphing).\n\n\n',
    'author': 'Jesse Smith',
    'author_email': 'jesseds@protonmail.ch',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://apav.readthedocs.io/en/latest/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8',
}


setup(**setup_kwargs)
