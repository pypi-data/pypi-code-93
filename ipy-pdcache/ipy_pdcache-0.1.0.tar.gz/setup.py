# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ipy_pdcache']

package_data = \
{'': ['*']}

install_requires = \
['ipython>=7.26.0,<8.0.0', 'pandas>=1.3.2,<2.0.0']

setup_kwargs = {
    'name': 'ipy-pdcache',
    'version': '0.1.0',
    'description': 'Automatically cache results of intensive computations in IPython.',
    'long_description': "# %%pdcache cell magic\n\n[![pypi version](https://img.shields.io/pypi/v/ipy-pdcache.svg)](https://pypi.org/project/ipy-pdcache/)\n[![Tests](https://github.com/kpj/ipy_pdcache/workflows/Tests/badge.svg)](https://github.com/kpj/ipy_pdcache/actions)\n\n\nAutomatically cache results of intensive computations in IPython.\n\nInspired by [ipycache](https://github.com/rossant/ipycache).\n\n\n## Installation\n\n```bash\n$ pip install ipy-pdcache\n```\n\n\n## Usage\n\nIn IPython:\n\n```python\nIn [1]: %load_ext ipy_pdcache\n\nIn [2]: import pandas as pd\n\nIn [3]: %%pdcache df data.csv\n   ...: df = pd.DataFrame({'A': [1,2,3], 'B': [4,5,6]})\n   ...:\n\nIn [4]: !cat data.csv\n,A,B\n0,1,4\n1,2,5\n2,3,6\n```\n\nThis will cache the dataframe and automatically load it when re-executing the cell.\n",
    'author': 'kpj',
    'author_email': 'kim.philipp.jablonski@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/kpj/ipy_pdcache',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.1,<4.0.0',
}


setup(**setup_kwargs)
