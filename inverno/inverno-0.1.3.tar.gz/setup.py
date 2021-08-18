# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['inverno']

package_data = \
{'': ['*'],
 'inverno': ['html/*',
             'html/css/*',
             'html/js/*',
             'html/js/demo/*',
             'html/js/src/*',
             'html/vendor/bootstrap/js/*',
             'html/vendor/bootstrap/scss/*',
             'html/vendor/bootstrap/scss/mixins/*',
             'html/vendor/bootstrap/scss/utilities/*',
             'html/vendor/bootstrap/scss/vendor/*',
             'html/vendor/chart.js/*',
             'html/vendor/datatables/*',
             'html/vendor/fontawesome-free/*',
             'html/vendor/fontawesome-free/css/*',
             'html/vendor/fontawesome-free/js/*',
             'html/vendor/fontawesome-free/less/*',
             'html/vendor/fontawesome-free/metadata/*',
             'html/vendor/fontawesome-free/scss/*',
             'html/vendor/fontawesome-free/sprites/*',
             'html/vendor/fontawesome-free/svgs/brands/*',
             'html/vendor/fontawesome-free/svgs/regular/*',
             'html/vendor/fontawesome-free/svgs/solid/*',
             'html/vendor/fontawesome-free/webfonts/*',
             'html/vendor/jquery-easing/*',
             'html/vendor/jquery/*',
             'project_template/*']}

install_requires = \
['CurrencyConverter>=0.16.1,<0.17.0',
 'Jinja2>=2.11.3,<3.0.0',
 'PyYAML>=5.4.1,<6.0.0',
 'click>=7.1.2,<8.0.0',
 'matplotlib>=3.4.1,<4.0.0',
 'pandas>=1.2.3,<2.0.0',
 'yfinance>=0.1.59,<0.2.0']

entry_points = \
{'console_scripts': ['inverno = inverno.cli:main']}

setup_kwargs = {
    'name': 'inverno',
    'version': '0.1.3',
    'description': 'Investments portfolio tracking tool',
    'long_description': None,
    'author': 'werew',
    'author_email': 'werew@ret2libc.com',
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
