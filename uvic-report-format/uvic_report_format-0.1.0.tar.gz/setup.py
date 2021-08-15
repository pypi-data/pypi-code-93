# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['uvic_report_format']

package_data = \
{'': ['*'], 'uvic_report_format': ['templates/*']}

install_requires = \
['Jinja2>=2.11.3,<3.0.0',
 'PyPDF2>=1.26.0,<2.0.0',
 'PyYAML>=5.4.1,<6.0.0',
 'click>=7.1.2,<8.0.0',
 'pydantic-yaml>=0.4.2,<0.5.0',
 'pydantic[email]>=1.8.2,<2.0.0',
 'pypandoc>=1.5,<2.0']

entry_points = \
{'console_scripts': ['uvic-report-compile = uvic_report_format.cli:compile',
                     'uvic-report-format = uvic_report_format.cli:cli']}

setup_kwargs = {
    'name': 'uvic-report-format',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Blake Smith',
    'author_email': 'blakeinvictoria@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
