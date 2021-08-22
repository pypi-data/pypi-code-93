# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['sm_widgets',
 'sm_widgets.models',
 'sm_widgets.services',
 'sm_widgets.widgets',
 'sm_widgets.widgets.annotator',
 'sm_widgets_integration']

package_data = \
{'': ['*'], 'sm_widgets.widgets': ['jscodes/*']}

install_requires = \
['elasticsearch>=7.12.1,<8.0.0',
 'fuzzywuzzy>=0.18.0,<0.19.0',
 'ipycallback>=0.2.5,<0.3.0',
 'kgdata>=1.1.8,<2.0.0',
 'loguru>=0.5.3,<0.6.0',
 'orjson>=3.5.2,<4.0.0',
 'python-slugify>=5.0.2,<6.0.0',
 'requests>=2.25.1,<3.0.0',
 'sem-desc>=0.1.9,<0.2.0',
 'tqdm>=4.60.0,<5.0.0']

setup_kwargs = {
    'name': 'sm-widgets',
    'version': '0.1.11',
    'description': '',
    'long_description': None,
    'author': 'Binh Vu',
    'author_email': 'binh@toan2.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
