# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['LbPlatformUtils']

package_data = \
{'': ['*'], 'LbPlatformUtils': ['bash-completion/*']}

entry_points = \
{'console_scripts': ['lb-debug-platform = LbPlatformUtils.debug:main',
                     'lb-describe-platform = LbPlatformUtils.describe:main',
                     'lb-host-binary-tag = '
                     'LbPlatformUtils.describe:host_binary_tag_script']}

setup_kwargs = {
    'name': 'lbplatformutils',
    'version': '4.3.8',
    'description': 'utilities for platform detection',
    'long_description': None,
    'author': 'CERN - LHCb Core Software',
    'author_email': 'lhcb-core-soft@cern.ch',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gitlab.cern.ch/lhcb-core/LbPlatformUtils',
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*',
}


setup(**setup_kwargs)
