# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['staircase',
 'staircase.core',
 'staircase.core.arrays',
 'staircase.core.ops',
 'staircase.core.stats',
 'staircase.docstrings',
 'staircase.io',
 'staircase.plotting',
 'staircase.util']

package_data = \
{'': ['*']}

install_requires = \
['matplotlib>=2', 'numpy>=1.12,<2.0', 'pytz']

extras_require = \
{':python_version < "3.9"': ['pandas>=0.24,<2'],
 ':python_version >= "3.9"': ['pandas>=1.1.3']}

setup_kwargs = {
    'name': 'staircase',
    'version': '2.0.0rc2',
    'description': 'Facilitating the modelling, manipulation and analysis of data with (mathematical) step functions',
    'long_description': '<p align="center"><a href="https://github.com/staircase-dev/staircase"><img src="https://github.com/staircase-dev/staircase/blob/master/docs/img/staircase.png?raw=true" title="staircase logo" alt="staircase logo"></a></p>\n\n\n<p align="center">\n\t<a href="https://pepy.tech/project/staircase/" alt="PyPI downloads">\n        <img src="https://pepy.tech/badge/staircase" /></a>\n    <a href="https://www.python.org/" alt="Python version">\n        <img src="https://img.shields.io/pypi/pyversions/staircase" /></a>\n    <a href="https://pypi.org/project/staircase/" alt="PyPI version">\n        <img src="https://img.shields.io/pypi/v/staircase" /></a>\n    <a href="https://anaconda.org/conda-forge/staircase" alt="Conda Forge version">\n        <img src="https://anaconda.org/conda-forge/staircase/badges/version.svg?branch=master&kill_cache=1" /></a>\n    <a href="https://github.com/staircase-dev/staircase/blob/master/LICENSE" alt="License">\n        <img src="http://img.shields.io/:license-mit-blue.svg?style=flat-square"></a>\n</p>\n<p align="center">\n\t<a href="https://github.com/staircase-dev/staircase/actions/workflows/ci.yml" alt"Github CI">\n\t\t<img src="https://github.com/staircase-dev/staircase/actions/workflows/ci.yml/badge.svg"/></a>\n    <a href="https://www.staircase.dev/en/latest/" alt="Documentation">\n        <img src="https://readthedocs.org/projects/railing/badge/?version=latest" /></a>\n\t<a href="https://app.codacy.com/gh/staircase-dev/staircase/dashboard" alt="Codacy Grade">\n        <img src="https://app.codacy.com/project/badge/Grade/845ecfb2fd6748cc87a66f9a97cd9492" /></a>\t\n\t<a href="https://app.codecov.io/gh/staircase-dev/staircase"  alt="Codecov coverage">\n\t\t<img src="https://codecov.io/gh/staircase-dev/staircase/branch/master/graph/badge.svg"/></a>\n</p>\n\n\nThe leading use-case for the staircase package is for the creation and analysis of step functions.\n\nPretty exciting huh.\n\nBut don\'t hit the close button on the browser just yet.  Let us convince you that much of the world around you can be modelled as step functions.\n\nFor example, the number of users viewing this page over time can be modelled as a step function.  The value of the function increases by 1 every time a user arrives at the page, and decreases by 1 every time a user leaves the page.  Let\'s say we have this data in vector format (i.e. tuple, list, numpy array, pandas series).  Specifically, assume *arrive* and *leave* are vectors of times, expressed as minutes past midnight, for all page views occuring yesterday.  Creating the corresponding step function is simple.  To achieve it we use the *[Stairs](https://www.staircase.dev/en/version2/reference/Stairs.html)* class:\n\n```python\n>>> import staircase as sc\n\n>>> views = sc.Stairs()\n>>> views.layer(arrive,leave)\n```\n\nWe can visualise the function with the plot function:\n```python\n>>> views.plot()\n```\n<p align="left"><img src="https://github.com/staircase-dev/staircase/blob/master/docs/img/pageviews.png?raw=true" title="pageviews example" alt="pageviews example"></p>\n\nWe can find the total time in minutes the page was viewed:\n```python\n>>> views.clip(0,1440).integral()\n9297.94622521079\n```\n\nWe can find the average number of viewers:\n```python\n>>> views.clip(0,1440).mean()\n6.4569071008408265\n```\n\nWe can find the average number of viewers, per hour of the day, and plot:\n```python\n>>> views.slice(pd.interval_range(0, periods=24, freq=60)).mean().plot()\n```\n<p align="left"><img src="https://github.com/staircase-dev/staircase/blob/master/docs/img/meanperhour.png?raw=true" title="mean page views per hour" alt="mean page views per hour"></p>\n\nWe can find the maximum concurrent views:\n```python\n>>> views.clip(0,1440).max()\n16\n```\n\nWe can create histogram data showing relative frequency of concurrent viewers (and plot it):\n```python\n>>> views.clip(0,1440).hist().plot.bar()\n```\n<p align="left"><img src="https://github.com/staircase-dev/staircase/blob/master/docs/img/pageviewshist.png?raw=true" title="concurrent viewers histogram" alt="concurrent viewers histogram"></p>\n\n\nPlotting is based on [matplotlib](https://matplotlib.org) and it requires relatively little effort to take the previous chart and improve the aesthetics:\n<p align="left"><img src="https://github.com/staircase/staircase/blob/master/docs/img/pageviewshistpretty.png?raw=true" title="concurrent viewers histogram (aesthetic)" alt="concurrent viewers histogram (aesthetic)"></p>\n\n\nThere is plenty more analysis that could be done.  The staircase package provides a rich variety of [arithmetic operations](https://www.staircase.dev/en/version2/reference/Stairs.html#arithmetic-operators), [relational operations](https://www.staircase.dev/en/version2/reference/Stairs.html#relational-operators), [logical operations](https://www.staircase.dev/en/version2/reference/Stairs.html#logical-operators), [statistical operations](https://www.staircase.dev/en/version2/reference/Stairs.html#statistical-operators), for use with *Stairs*, in addition to functions for [univariate analysis](https://www.staircase.dev/en/version2/reference/Stairs.html#summary-statistics), [aggregations](https://www.staircase.dev/en/version2/reference/arrays.html#aggregation) and compatibility with [pandas.Timestamp](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.Timestamp.html).\n\n\n## Installation\n\nstaircase can be installed from PyPI:\n\n```bash\npython -m pip install staircase\n```\n\nor also with conda:\n\n```bash\nconda install -c conda-forge staircase\n```\n\n## Documentation\nThe complete guide to using staircase can be found at [staircase.dev](https://www.staircase.dev)\n\n## Contributing\nThere are many ways in which contributions can be made - the first and foremost being *using staircase and giving feedback*.\n\nBug reports, feature requests and ideas can be submitted via the [Github issue tracker](https://github.com/staircase-dev/staircase/issues).\n\nAdditionally, bug fixes. enhancements, and improvements to the code and documentation are also appreciated and can be done via pull requests.\nTake a look at the current issues and if there is one you would like to work on please leave a comment to that effect.\n\nSee this [beginner\'s guide to contributing](https://github.com/firstcontributions/first-contributions), or [Pandas\' guide to contributing](https://pandas.pydata.org/pandas-docs/stable/development/contributing.html), to learn more about the process.\n\n\n## Versioning\n\nWe use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/staircase-dev/staircase/tags). \n\n\n## License\n\nThis project is licensed under the MIT License - see the [LICENSE](https://github.com/staircase-dev/staircase/blob/master/LICENSE) file for details\n\n## Acknowledgments\n\nThe seeds of *staircase* began developing at the Hunter Valley Coal Chain Coordinator, where it finds strong application in analysing simulated data.  Thanks for the support!',
    'author': 'Riley Clement',
    'author_email': 'venaturum@gmail.com',
    'maintainer': 'Riley Clement',
    'maintainer_email': 'venaturum@gmail.com',
    'url': 'https://github.com/staircase-dev/staircase',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
