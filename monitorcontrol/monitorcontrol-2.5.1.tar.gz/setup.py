# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['monitorcontrol', 'monitorcontrol.vcp']

package_data = \
{'': ['*']}

extras_require = \
{':python_version <= "3.7"': ['importlib_metadata>=2,<5'],
 ':sys_platform != "win32"': ['pyudev>=0.22.0,<0.23.0']}

entry_points = \
{'console_scripts': ['monitorcontrol = monitorcontrol.__main__:main']}

setup_kwargs = {
    'name': 'monitorcontrol',
    'version': '2.5.1',
    'description': 'Monitor controls using MCCS over DDC-CI.',
    'long_description': 'monitorcontrol\n##############\n\n|PyPi Version| |Build Status| |Documentation Status| |Coverage Status| |Black|\n\nPython monitor control using the VESA Monitor Control Command Set (MCCS)\nover the Display Data Channel Command Interface Standard (DDC-CI).\n\nSupported Platforms\n*******************\n-  Linux (tested with Ubuntu desktop 20.04 LTS)\n-  Windows (tested with Windows 10)\n\nWindows Install\n***************\n\n.. code-block:: bash\n\n   py -3.8 -m pip install monitorcontrol\n\nLinux Install\n*************\n\n.. code-block:: bash\n\n   python3.8 -m pip install monitorcontrol\n\nDocumentation\n*************\n\nFull documentation including examples is available on readthedocs\n`here <https://monitorcontrol.readthedocs.io/en/latest/>`__.\n\n.. |PyPi Version| image:: https://badge.fury.io/py/monitorcontrol.svg\n   :target: https://badge.fury.io/py/monitorcontrol\n.. |Build Status| image:: https://travis-ci.com/newAM/monitorcontrol.svg?branch=master\n   :target: https://travis-ci.com/newAM/monitorcontrol\n.. |Coverage Status| image:: https://coveralls.io/repos/github/newAM/monitorcontrol/badge.svg?branch=master\n   :target: https://coveralls.io/github/newAM/monitorcontrol?branch=master\n.. |Documentation Status| image:: https://readthedocs.org/projects/monitorcontrol/badge/?version=latest\n   :target: https://monitorcontrol.readthedocs.io/en/latest/?badge=latest\n.. |Black| image:: https://img.shields.io/badge/code%20style-black-000000.svg\n   :target: https://github.com/psf/black\n',
    'author': 'Alex M.',
    'author_email': 'alexmgit@protonmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/newAM/monitorcontrol',
    'packages': packages,
    'package_data': package_data,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
