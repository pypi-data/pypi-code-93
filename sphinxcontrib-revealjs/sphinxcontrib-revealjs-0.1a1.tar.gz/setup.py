# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['sphinxcontrib', 'sphinxcontrib.revealjs', 'sphinxcontrib.revealjs.directives']

package_data = \
{'': ['*'],
 'sphinxcontrib.revealjs': ['theme/*',
                            'theme/revealjs_themes/*',
                            'theme/static/*']}

install_requires = \
['Sphinx>=4.1.1,<5.0.0', 'cssutils>=2.3.0,<3.0.0']

setup_kwargs = {
    'name': 'sphinxcontrib-revealjs',
    'version': '0.1a1',
    'description': 'Build slides with RevealJS.',
    'long_description': None,
    'author': 'Ashley Trinh',
    'author_email': 'ashley@hackbrightacademy.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
