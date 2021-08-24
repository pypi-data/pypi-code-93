# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['munge', 'munge.codec']

package_data = \
{'': ['*']}

install_requires = \
['click>=5.1', 'requests>=2.6,<3.0']

extras_require = \
{'toml': ['toml>=0.10.2,<0.11.0'],
 'tomlkit': ['tomlkit>=0.7.2,<0.8.0'],
 'yaml': ['PyYAML>=5.1,<6.0']}

entry_points = \
{'console_scripts': ['munge = munge.cli:main']}

setup_kwargs = {
    'name': 'munge',
    'version': '1.2.1',
    'description': 'data manipulation library and client',
    'long_description': '# munge\n\n[![PyPI](https://img.shields.io/pypi/v/munge.svg?maxAge=3600)](https://pypi.python.org/pypi/munge)\n[![PyPI](https://img.shields.io/pypi/pyversions/munge.svg?maxAge=600)](https://pypi.python.org/pypi/munge)\n[![Tests](https://github.com/20c/munge/workflows/tests/badge.svg)](https://github.com/20c/munge)\n[![LGTM Grade](https://img.shields.io/lgtm/grade/python/github/20c/munge)](https://lgtm.com/projects/g/20c/munge/alerts/)\n[![Codecov](https://img.shields.io/codecov/c/github/20c/munge/master.svg?maxAge=3600)](https://codecov.io/github/20c/munge?branch=master)\n\ndata manipulation library and client\n\n## Changes\n\nThe current change log is available at <https://github.com/20c/munge/blob/master/CHANGELOG.md>\n\n\n## License\n\nCopyright 2015-2021 20C, LLC\n\nLicensed under the Apache License, Version 2.0 (the "License");\nyou may not use this softare except in compliance with the License.\nYou may obtain a copy of the License at\n\n   http://www.apache.org/licenses/LICENSE-2.0\n\nUnless required by applicable law or agreed to in writing, software\ndistributed under the License is distributed on an "AS IS" BASIS,\nWITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.\nSee the License for the specific language governing permissions and\nlimitations under the License.',
    'author': '20C',
    'author_email': 'code@20c.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/20c/munge/',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
