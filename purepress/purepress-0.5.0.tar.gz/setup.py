# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['purepress']

package_data = \
{'': ['*']}

install_requires = \
['Flask>=1.1.2,<2.0.0',
 'Markdown>=3.2.2,<3.3.0',
 'PyYAML>=5.3.1,<5.4.0',
 'Werkzeug>=1.0.1,<2.0.0',
 'click>=7.1.2,<8.0.0',
 'colorama>=0.4.3,<0.5.0',
 'feedgen>=0.9.0,<0.10.0',
 'html-toc>=0.1.1,<0.2.0',
 'py-gfm>=1.0.0,<1.1.0',
 'pytz>=2020.1,<2021.0',
 'toml>=0.10.2,<0.11.0']

entry_points = \
{'console_scripts': ['purepress = purepress.__main__:main']}

setup_kwargs = {
    'name': 'purepress',
    'version': '0.5.0',
    'description': 'A simple static blog generator.',
    'long_description': '# PurePress\n\n[![PyPI](https://img.shields.io/pypi/v/purepress.svg)](https://pypi.python.org/pypi/purepress)\n![Python](https://img.shields.io/badge/python-3.6%2B-blue.svg)\n\n**PurePress** is a very simple static blog generator.\n\n## Usage\n\n```bash\npip install purepress\n\nmkdir my-blog\ncd my-blog\n\npurepress init  # init the blog\ngit clone https://github.com/verilab/purepress-theme-default.git theme  # install a theme\n\npurepress preview  # preview the blog\npurepress build  # build the blog\n```\n\nSee [richardchien/project-rc](https://github.com/richardchien/project-rc) for more usage.\n',
    'author': 'Richard Chien',
    'author_email': 'richardchienthebest@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/verilab/purepress',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
