# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pyenvnoise', 'pyenvnoise.utils']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.18.1']

setup_kwargs = {
    'name': 'pyenvnoise',
    'version': '0.1.2',
    'description': 'A package for environmental noise analysis',
    'long_description': "Environmental noise analysis in Python\n=====================\n\n[![Language](https://img.shields.io/badge/python-v3.7-green.svg)](https://www.python.org/)\n[![License](https://img.shields.io/badge/license-MIT-green.svg)](https://github.com/ducphucnguyen/PyEnvNoise/blob/master/LICENSE)\n\nThe library contains:\n\n- `utils.*`: comprehensive sets of functions for pre- and post-signal processing\n\n\n## install\n\nInstall latest version:\n\n- `pip install pyenvnoise==0.1.1`\n\nLatest development version from git:\n\n```\npip install poetry # if not already installed\npip install git+https://github.com/ducphucnguyen/PyEnvNoise.git\n```\n\n## Read *.pti files\n\nA fastest method to read acoustic files with *.pti extension\n\n```python\nimport pyenvnoise\nfrom pyenvnoise.utils import ptiread\n\n# read .pti files\n# output:\n# signal: array(lengh samples, numbers of channels)\n# fs: sampling frequency\n# t: time of files\n# d: date of file\nsignal, fs, t, d = ptiread('Recording-1.1.pti')\n\n",
    'author': 'Phuc D. Nguyen',
    'author_email': 'ducphuc.nguyen@flinders.edu.au',
    'maintainer': 'Phuc D. Nguyen',
    'maintainer_email': 'ducphuc.nguyen@flinders.edu.au',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
