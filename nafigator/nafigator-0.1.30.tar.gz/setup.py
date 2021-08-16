# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nafigator']

package_data = \
{'': ['*']}

install_requires = \
['FoLiA>=2.5.5,<3.0.0',
 'click>=7.0',
 'lxml>=4.6.3,<5.0.0',
 'pdfminer.six>=20201018,<20201019',
 'python-docx>=0.8.11,<0.9.0']

setup_kwargs = {
    'name': 'nafigator',
    'version': '0.1.30',
    'description': 'Python package to convert spaCy and Stanza documents to NLP Annotation Format (NAF)',
    'long_description': None,
    'author': 'Willem Jan Willemse',
    'author_email': 'w.j.willemse@xs4all.nl',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
