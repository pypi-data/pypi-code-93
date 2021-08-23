# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['researchhelper',
 'researchhelper.analyse',
 'researchhelper.datastructures',
 'researchhelper.decorators',
 'researchhelper.modeling',
 'researchhelper.optimize',
 'researchhelper.processdata',
 'researchhelper.visualize']

package_data = \
{'': ['*']}

install_requires = \
['matplotlib>=3.4.0,<4.0.0',
 'networkx>=2.6.2,<3.0.0',
 'numpy>=1.20.1,<2.0.0',
 'pydantic>=1.8.2,<2.0.0',
 'scipy>=1.6.2,<2.0.0',
 'tqdm>=4.62.1,<5.0.0']

setup_kwargs = {
    'name': 'researchhelper',
    'version': '0.1.7',
    'description': 'A repository of useful functions supporting research.',
    'long_description': '# Table of Contents\n\n1.  [Welcome to ResearchHelper](#orga7ce240)\n2.  [Sphinx, Pypi](#org6b44add)\n\n\n<a id="orga7ce240"></a>\n\n# Welcome to ResearchHelper\n\nThis is a personal repository of functions that I use throughout projects. Besides that, it could obviously also be useful to others! So see if it holds something for you.\n\n\n<a id="org6b44add"></a>\n\n# Sphinx, Pypi\n\nThis package is not only for my functionality, but also to practice in making a package and documenting is correctly. For that I\'m using Sphinx. The online hosted documentation is found on my website <https://www.baschatel.nl/ResearchHelper>.\n',
    'author': 'Bas Chatel',
    'author_email': 'bastiaan.chatel@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://www.baschatel.nl/researchhelper',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
