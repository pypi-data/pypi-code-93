# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['ardutest']

package_data = \
{'': ['*']}

install_requires = \
['MAVProxy>=1.8.38,<2.0.0',
 'docker>=5.0.0,<6.0.0',
 'dronekit>=2.9.2,<3.0.0',
 'numpy>=1.20.3,<2.0.0',
 'partx==0.0.41',
 'psy-taliro==1.0.0a12',
 'pydantic>=1.8.2,<2.0.0',
 'pymavlink==2.4.8']

entry_points = \
{'console_scripts': ['ardutest = ardutest.__main__:ardutest']}

setup_kwargs = {
    'name': 'ardutest',
    'version': '0.1.0a0',
    'description': 'Wrapper around the arductl library to run falsifications using PSY-Taliro',
    'long_description': None,
    'author': 'Aniruddh Chandratre',
    'author_email': 'achand75@asu.edu',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7.1,<3.10',
}


setup(**setup_kwargs)
