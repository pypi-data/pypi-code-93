# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['coco_assistant', 'coco_assistant.utils', 'tests']

package_data = \
{'': ['*']}

install_requires = \
['coco-ash>=2.0.2,<3.0.0',
 'matplotlib>=3.4.2,<4.0.0',
 'pandas>=1.3.1,<2.0.0',
 'requests>=2.26.0,<3.0.0',
 'seaborn>=0.11.1,<0.12.0',
 'tqdm>=4.62.0,<5.0.0']

extras_require = \
{'dev': ['tox>=3.20.1,<4.0.0',
         'virtualenv>=20.2.2,<21.0.0',
         'pip>=20.3.1,<21.0.0',
         'twine>=3.3.0,<4.0.0',
         'pre-commit>=2.12.0,<3.0.0',
         'toml>=0.10.2,<0.11.0'],
 'doc': ['livereload[doc]>=2.6.3,<3.0.0',
         'mkdocs>=1.1.2,<2.0.0',
         'mkdocs-include-markdown-plugin>=1.0.0,<2.0.0',
         'mkdocs-material>=7.1.0,<8.0.0',
         'mkdocstrings>=0.13.6,<0.14.0',
         'mkdocs-literate-nav[doc]>=0.4.0,<0.5.0',
         'mkdocs-gen-files[doc]>=0.3.3,<0.4.0',
         'mkdocs-section-index[doc]>=0.3.1,<0.4.0',
         'mkdocs-autorefs==0.1.1'],
 'test': ['black==20.8b1',
          'isort==5.6.4',
          'flake8==3.8.4',
          'flake8-docstrings>=1.6.0,<2.0.0',
          'pytest>=6.2.0,<7.0.0',
          'pytest-cov>=2.10.1,<3.0.0',
          'coverage>=5.5,<6.0']}

entry_points = \
{'console_scripts': ['coco-assistant = coco_assistant.cli:main']}

setup_kwargs = {
    'name': 'coco-assistant',
    'version': '0.4.0',
    'description': 'Helper for dealing with MS-COCO annotations.',
    'long_description': '# COCO-Assistant\n\n![CircleCI](https://img.shields.io/circleci/build/github/ashnair1/COCO-Assistant?&label=Build&logo=CircleCI)\n[![Codacy Badge](https://img.shields.io/codacy/grade/5299d18c95da4991b4f3a6ae6e8a0b7a/master?label=Code%20Quality&logo=Codacy)](https://app.codacy.com/gh/ashnair1/COCO-Assistant/dashboard)\n[![Code style: black](https://img.shields.io/badge/Code%20Style-black-000000.svg)](https://github.com/psf/black)\n[![PyPi License](https://img.shields.io/pypi/v/coco-assistant?branch=master&label=PyPi%20Version&logo=PyPi&logoColor=ffffff&labelColor=306998&color=FFD43B&style=flat)](https://pypi.org/project/coco-assistant/)\n[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://img.shields.io/github/license/ashnair1/COCO-Assistant?color=yellow&label=License&logo=MIT)\n\nHelper for dealing with MS-COCO annotations.\n\n## Overview\n\nThe MS COCO annotation format along with the pycocotools library is quite\npopular among the computer vision community. Yet I for one found it difficult to\nplay around with the annotations. Deleting a specific category, combining\nmultiple mini datasets to generate a larger dataset, viewing distribution of\nclasses in the annotation file are things I would like to do without writing a\nseparate script for each scenario.\n\nThe COCO Assistant is designed (or being designed) to assist with this problem.\n**Please note that currently, the Assistant can only help out with object\ndetection datasets**. Any contributions and/or suggestions are welcome.\n\n## Package features\n\nCOCO-Assistant currently supports the following features:\n\n-   Merge datasets.\n-   Remove specfiic category from dataset.\n-   Generate annotations statistics - distribution of object areas and category distribution.\n-   Annotation visualiser for viewing the entire dataset.\n',
    'author': 'Ashwin Nair',
    'author_email': 'ashnair0007@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ashnair1/coco_assistant',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7.1,<4.0',
}


setup(**setup_kwargs)
