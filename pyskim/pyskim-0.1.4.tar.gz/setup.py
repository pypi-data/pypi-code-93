# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pyskim']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.0.1,<9.0.0',
 'ipython>=7.26.0,<8.0.0',
 'numpy>=1.21.2,<2.0.0',
 'pandas>=1.3.2,<2.0.0',
 'scipy>=1.7.1,<2.0.0',
 'tabulate>=0.8.9,<0.9.0']

entry_points = \
{'console_scripts': ['pyskim = pyskim:main']}

setup_kwargs = {
    'name': 'pyskim',
    'version': '0.1.4',
    'description': 'Quickly create summary statistics for a given dataframe.',
    'long_description': "# pyskim\n\n[![PyPI](https://img.shields.io/pypi/v/pyskim.svg?style=flat)](https://pypi.python.org/pypi/pyskim)\n[![Tests](https://github.com/kpj/pyskim/actions/workflows/main.yaml/badge.svg)](https://github.com/kpj/pyskim/actions/workflows/main.yaml)\n\nQuickly create summary statistics for a given dataframe.\n\nThis package aspires to be as awesome as [skimr](https://github.com/ropensci/skimr).\n\n\n## Installation\n\n```bash\n$ pip install pyskim\n```\n\n## Usage\n\n### Commandline tool\n\n\n`pyskim` can be used from the commandline:\n\n```bash\n$ pyskim iris.csv\n── Data Summary ────────────────────────────────────────────────────────────────────────────────────\ntype                 value\n-----------------  -------\nNumber of rows         150\nNumber of columns        5\n──────────────────────────────────────────────────\nColumn type frequency:\n           Count\n-------  -------\nFloat64        4\nstring         1\n\n── Variable type: number ───────────────────────────────────────────────────────────────────────────\n    name            na_count    mean     sd    p0    p25    p50    p75    p100  hist\n--  ------------  ----------  ------  -----  ----  -----  -----  -----  ------  ----------\n 0  sepal_length           0    5.84  0.828   4.3    5.1   5.8     6.4     7.9  ▂▆▃▇▄▇▅▁▁▁\n 1  sepal_width            0    3.06  0.436   2      2.8   3       3.3     4.4  ▁▁▄▅▇▆▂▂▁▁\n 2  petal_length           0    3.76  1.77    1      1.6   4.35    5.1     6.9  ▇▃▁▁▂▅▆▄▃▁\n 3  petal_width            0    1.2   0.762   0.1    0.3   1.3     1.8     2.5  ▇▂▁▂▂▆▁▄▂▃\n\n── Variable type: string ───────────────────────────────────────────────────────────────────────────\n    name       na_count    n_unique  top_counts\n--  -------  ----------  ----------  -----------------------------------------\n 0  species           0           3  setosa: 50, versicolor: 50, virginica: 50\n```\n\nFull overview:\n\n```bash\n$ pyskim --help\nUsage: pyskim [OPTIONS] <file>\n\n  Quickly create summary statistics for a given dataframe.\n\nOptions:\n  -d, --delimiter TEXT   Delimiter of file.\n  -i, --interactive      Open prompt with dataframe as `df` after displaying\n                         summary.\n\n  --no-dtype-conversion  Skip automatic dtype conversion.\n  --help                 Show this message and exit.\n```\n\n### Python API\n\nAlternatively, it is possible to use it in code:\n\n```python\n>>> from pyskim import skim\n>>> from seaborn import load_dataset\n\n>>> iris = load_dataset('iris')\n>>> skim(iris)\n# ── Data Summary ────────────────────────────────────────────────────────────────────────────────────\n# type                 value\n# -----------------  -------\n# Number of rows         150\n# Number of columns        5\n# ──────────────────────────────────────────────────\n# Column type frequency:\n#            Count\n# -------  -------\n# float64        4\n# string         1\n#\n# ── Variable type: number ───────────────────────────────────────────────────────────────────────────\n#     name            na_count    mean     sd    p0    p25    p50    p75    p100  hist\n# --  ------------  ----------  ------  -----  ----  -----  -----  -----  ------  ----------\n#  0  sepal_length           0    5.84  0.828   4.3    5.1   5.8     6.4     7.9  ▂▆▃▇▄▇▅▁▁▁\n#  1  sepal_width            0    3.06  0.436   2      2.8   3       3.3     4.4  ▁▁▄▅▇▆▂▂▁▁\n#  2  petal_length           0    3.76  1.77    1      1.6   4.35    5.1     6.9  ▇▃▁▁▂▅▆▄▃▁\n#  3  petal_width            0    1.2   0.762   0.1    0.3   1.3     1.8     2.5  ▇▂▁▂▂▆▁▄▂▃\n#\n# ── Variable type: string ───────────────────────────────────────────────────────────────────────────\n#     name               na_count    n_unique  top_counts\n# --  ---------------  ----------  ----------  -----------------------------------------\n#  0          species           0           3  versicolor: 50, setosa: 50, virginica: 50\n```\n",
    'author': 'kpj',
    'author_email': 'kim.philipp.jablonski@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/kpj/pyskim',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7.1,<3.10',
}


setup(**setup_kwargs)
