# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['multimd']

package_data = \
{'': ['*']}

install_requires = \
['natsort>=7.1.1,<8.0.0']

setup_kwargs = {
    'name': 'multimd',
    'version': '0.0.0b0',
    'description': 'This project makes it possible to write separated pieces of ``MD`` files that will be merged to produce one single final ``MD`` file.',
    'long_description': 'The `Python` module `multimd`\n=============================\n\n\n> **I beg your pardon for my english...**\n>\n> English is not my native language, so be nice if you notice misunderstandings, misspellings, or grammatical errors in my documents and codes.\n\n\nAbout `multimd`\n---------------\n\nWorking with `MD` documents of moderate size in a single file can becomes quickly painful. This project makes it possible to write separated pieces of `MD` files that will be merged to produce one single  `MD` file.\n\n\n<!-- :tutorial-START: -->\n<!-- :tutorial-END: -->\n\n\n<!-- :version-START: -->\n<!-- :version-END: -->\n',
    'author': 'Christophe BAL',
    'author_email': None,
    'maintainer': 'Christophe BAL',
    'maintainer_email': None,
    'url': 'https://github.com/projetmbc/tools-for-dev/tree/master/multimd',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
