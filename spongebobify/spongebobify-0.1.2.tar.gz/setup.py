# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['spongebobify']

package_data = \
{'': ['*']}

install_requires = \
['typer>=0.3.2,<0.4.0']

entry_points = \
{'console_scripts': ['spongebobify = spongebobify.main:app']}

setup_kwargs = {
    'name': 'spongebobify',
    'version': '0.1.2',
    'description': 'Are ya ready kids? aYE AyE! You can now make your text...sARcaStiC!',
    'long_description': '# Spongebobify\n\nMake some text sarcastic!\nmAkE soMe TExT sARcAsTIC!\n',
    'author': 'Michael Gray',
    'author_email': 'mike@graywind.org',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/mikejgray/spongebobify',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
