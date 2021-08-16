# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['canvas_cli', 'canvas_cli.dev']

package_data = \
{'': ['*'],
 'canvas_cli.dev': ['cms125v6_woman_due/*',
                    'cms125v6_woman_mammography/*',
                    'cms125v6_woman_mastectomy/*']}

install_requires = \
['arrow>=1.1.1,<2.0.0',
 'click>=8.0.1,<9.0.0',
 'python-decouple>=3.4,<4.0',
 'requests>=2.26.0,<3.0.0']

setup_kwargs = {
    'name': 'canvas-cli',
    'version': '1.3.0',
    'description': 'A command-line tool for the Canvas Medical EMR system.',
    'long_description': None,
    'author': 'Beau Gunderson',
    'author_email': 'beaugunderson@github-username.x',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
