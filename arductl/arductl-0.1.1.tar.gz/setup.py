# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['arductl']

package_data = \
{'': ['*']}

install_requires = \
['MAVProxy>=1.8.38,<2.0.0',
 'attrs>=21.0.0,<22.0.0',
 'cattrs>=1.7.1,<2.0.0',
 'docker>=5.0.0,<6.0.0',
 'dronekit-sitl>=3.3.0,<4.0.0',
 'dronekit>=2.9.2,<3.0.0',
 'numpy>=1.20.3,<2.0.0',
 'pydantic>=1.8.2,<2.0.0',
 'pymavlink==2.4.8']

setup_kwargs = {
    'name': 'arductl',
    'version': '0.1.1',
    'description': 'Helper Library to execute ArduPilot simulations using a Docker Container and dronekit.',
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
    'python_requires': '>=3.7.1,<3.10',
}


setup(**setup_kwargs)
