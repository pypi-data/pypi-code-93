# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['hyperc', 'hyperc.examples']

package_data = \
{'': ['*']}

install_requires = \
['dill>=0.3.2',
 'diskcache>=4.1.0,<5.0.0',
 'downward_ch>=0.0.9',
 'formulas>=1.0.0,<2.0.0',
 'psutil>=5.7',
 'unidecode>=1.1.1',
 'wrapt==1.11.2']

entry_points = \
{'console_scripts': ['hc = hyperc.hc:main']}

setup_kwargs = {
    'name': 'hyperc',
    'version': '0.0.1',
    'description': 'Python AI Planning and automated programming',
    'long_description': '# hyperc\n# test\n\n`pytest`\n',
    'author': 'Andrew Gree',
    'author_email': 'andrew@hyperc.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/hyperc-ai/hyperc',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7',
}


setup(**setup_kwargs)
