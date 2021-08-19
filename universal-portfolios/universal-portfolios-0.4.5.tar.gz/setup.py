# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['universal', 'universal.algos', 'universal.algos.ternary']

package_data = \
{'': ['*'],
 'universal': ['data/djia.csv',
               'data/djia.csv',
               'data/djia.csv',
               'data/djia.csv',
               'data/djia.csv',
               'data/djia.csv',
               'data/jpm_assumptions/*',
               'data/msci.csv',
               'data/msci.csv',
               'data/msci.csv',
               'data/msci.csv',
               'data/msci.csv',
               'data/msci.csv',
               'data/nyse_n.csv',
               'data/nyse_n.csv',
               'data/nyse_n.csv',
               'data/nyse_n.csv',
               'data/nyse_n.csv',
               'data/nyse_n.csv',
               'data/nyse_o.csv',
               'data/nyse_o.csv',
               'data/nyse_o.csv',
               'data/nyse_o.csv',
               'data/nyse_o.csv',
               'data/nyse_o.csv',
               'data/sp500.csv',
               'data/sp500.csv',
               'data/sp500.csv',
               'data/sp500.csv',
               'data/sp500.csv',
               'data/sp500.csv',
               'data/tse.csv',
               'data/tse.csv',
               'data/tse.csv',
               'data/tse.csv',
               'data/tse.csv',
               'data/tse.csv']}

install_requires = \
['cvxopt==1.2.5',
 'matplotlib>=3.3.1,<4.0.0',
 'pandas-datareader>=0.10.0,<0.11.0',
 'pandas>=1.1.1,<2.0.0',
 'plotly>=4.9.0,<5.0.0',
 'requests>=2.24.0,<3.0.0',
 'scikit-learn>=0.23.2,<0.24.0',
 'scipy>=1.5.2,<2.0.0',
 'seaborn>=0.10.1,<0.11.0',
 'statsmodels>=0.12.0,<0.13.0',
 'tqdm>=4.56.2,<5.0.0']

setup_kwargs = {
    'name': 'universal-portfolios',
    'version': '0.4.5',
    'description': 'Collection of algorithms for online portfolio selection',
    'long_description': '# Universal Portfolios\n\n![PyPi Version](https://img.shields.io/pypi/v/universal-portfolios?style=flat-square)\n![PyPi License](https://img.shields.io/pypi/l/universal-portfolios?style=flat-square)\n![PyPi Downloads](https://img.shields.io/pypi/dm/universal-portfolios?style=flat-square)\n\n![Open PRs](https://img.shields.io/github/issues-pr-raw/Marigold/universal-portfolios?style=flat-square)\n![Contributors](https://img.shields.io/badge/contributors-9-orange.svg?style=flat-square)\n![Repo size](https://img.shields.io/github/repo-size/Marigold/universal-portfolios?style=flat-square)\n\n\nThe purpose of this Python package is to put together different Online Portfolio Selection (OLPS) algorithms and provide unified tools for their analysis.\n\n\nIn short, the purpose of OLPS is to _choose portfolio weights in every period to maximize its final wealth_. Examples of such portfolios could be the [Markowitz portfolio](http://en.wikipedia.org/wiki/Modern_portfolio_theory) or the [Universal portfolio](http://en.wikipedia.org/wiki/Universal_portfolio_algorithm). There is currently an active research in the area of online portfolios and even though the results are mostly theoretical, algorithms for practical use start to appear.\n\nSeveral state-of-the-art algorithms are implemented, based on my understanding of the available literature. Contributions or corrections are more than welcomed.\n\n## Outline of this package\n\n* `examples` contains two Python Notebooks:\n   - [Online Portfolios](http://nbviewer.ipython.org/github/Marigold/universal-portfolios/blob/master/On-line%20portfolios.ipynb) : explains the basic use of the library. Script sequence, various options, method arguments, and a strategy template to get you started.\n   - [Modern Portfolio Theory](http://nbviewer.ipython.org/github/Marigold/universal-portfolios/blob/master/modern-portfolio-theory.ipynb) : goes deeper into the OLPS principle and the tools developped in this library to approach it.\n\n* `universal.data` contains various datasets to help you in your journey\n\n* `universal.algos` hosts the implementations of various OLPS algorithms from the litterature :\n\n<div align="center">\n\n| Benchmarks | Follow the winner | Follow the loser | Pattern matching | Other |\n|---|---|---|---|---|\n| __[BAH](https://github.com/Marigold/universal-portfolios/blob/master/universal/algos/bah.py)__ | __[Universal Portfolios](https://github.com/Marigold/universal-portfolios/blob/master/universal/algos/up.py)__ | __[Anticorr](https://github.com/Marigold/universal-portfolios/blob/master/universal/algos/anticor.py)__ | __[BNN](https://github.com/Marigold/universal-portfolios/blob/master/universal/algos/bnn.py)__ | __[Markovitz](https://github.com/Marigold/universal-portfolios/blob/master/universal/algos/best_markowitz.py)__ |\n| __[CRP](https://github.com/Marigold/universal-portfolios/blob/master/universal/algos/crp.py)__ | __[Exponential Gradient](https://github.com/Marigold/universal-portfolios/blob/master/universal/algos/eg.py)__ | __[PAMR](https://github.com/Marigold/universal-portfolios/blob/master/universal/algos/pamr.py)__ | __[CORN](https://github.com/Marigold/universal-portfolios/blob/master/universal/algos/corn.py)__ | __[Kelly](https://github.com/Marigold/universal-portfolios/blob/master/universal/algos/kelly.py)__ |\n| __[BCRP](https://github.com/Marigold/universal-portfolios/blob/master/universal/algos/bcrp.py)__ || __[OLMAR](https://github.com/Marigold/universal-portfolios/blob/master/universal/algos/olmar.py)__ || __[Best so far](https://github.com/Marigold/universal-portfolios/blob/master/universal/algos/best_so_far.py)__ |\n| __[DCRP](https://github.com/Marigold/universal-portfolios/blob/master/universal/algos/dynamic_crp.py)__ || __[RMR](https://github.com/Marigold/universal-portfolios/blob/master/universal/algos/rmr.py)__ || __[ONS](https://github.com/Marigold/universal-portfolios/blob/master/universal/algos/ons.py)__ |\n||| __[CWMR](https://github.com/Marigold/universal-portfolios/blob/master/universal/algos/cwmr.py)__ || __[MPT](https://github.com/Marigold/universal-portfolios/blob/master/universal/algos/mpt.py)__ |\n||| __[WMAMR](https://github.com/Marigold/universal-portfolios/blob/master/universal/algos/wmamr.py)__ |||\n||| __[RPRT](https://github.com/Marigold/universal-portfolios/blob/master/universal/algos/rprt.py)__ |||\n\n</div>\n\n\n* `universal.algo` provides a general class inherited by all the individual algos\' subclasses. Algo computes the weights at every timestep.\n\n* `universal.result` computes the portfolio wealth from the weights and various metrics on the strategy\'s performance.\n\n\n## Quick Start\n\n```python\nfrom universal import tools\nfrom universal.algos import CRP\n\nif __name__ == \'__main__\':\n  # Run CRP on a computed-generated portfolio of 3 stocks and plot the results\n  tools.quickrun(CRP())\n\n```\n\n\n## Additional Resources\n\nIf you do not know what online portfolio is, look at [Ernest Chan blog](http://epchan.blogspot.cz/2007/01/universal-portfolios.html), [CASTrader](http://www.castrader.com/2006/11/universal_portf.html) or a recent [survey by Bin Li and Steven C. H. Hoi](http://arxiv.org/abs/1212.2129).\n\nPaul Perry followed up on this and made a [comparison of all algorithms](http://nbviewer.ipython.org/github/paulperry/quant/blob/master/OLPS_Comparison.ipynb) on more recent ETF datasets. The original authors of some of the algorithms recently published their own implementation on GitHub - [Online Portfolio Selection Toolbox](https://github.com/OLPS/OLPS) in MATLAB.\n\nIf you are more into R or just looking for a good resource about Universal Portfolios, check out blog and package [logopt](http://optimallog.blogspot.cz/) by Marc Delvaux.\n\nNote : If you don\'t want to install the package locally, you can run both notebooks with Binder - [modern-portfolio-theory.ipynb ![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/Marigold/universal-portfolios/master?filepath=modern-portfolio-theory.ipynb) or [On-line portfolios.ipynb ![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/Marigold/universal-portfolios/master?filepath=On-line%20portfolios.ipynb)\n\n## Installation\n\nOnly Python 3 is supported\n\n```\npip install universal-portfolios\n```\n\n## Development\n\n[poetry](https://python-poetry.org/) is used to manage the dependencies. Run `poetry install` to install a virtual environment and then `poetry shell` to launch it.\n\nExporting dependencies to the `requirements.txt` file is needed for mybinder.org. It is done via\n\n```\npoetry export --without-hashes -f requirements.txt > requirements.txt\npoetry export --dev --without-hashes -f requirements.txt > test-requirements.txt\n```\n\n### Formatting\n\nWe use pre-commit hook to automatically format code and check for linting errors before each commit. If the checks fail you need to resolve the errors and amend the change set.\n\nTo setup the pre-commit hooks you need to [install it first](https://pre-commit.com/#installation) and then enter the project root directory and invoke the command (only once!):\n\n```\npre-commit install\n```\n\n\n## Running Tests\n\n```\npoetry run python -m pytest --capture=no --ff -x tests/\n```\n\n## Contributors\n\nCreator : [Marigold](https://github.com/Marigold)\n\n_Thank you for your contributions!_\n\n[Alexander Myltsev](https://github.com/alexander-myltsev) | [angonyfox](https://github.com/angonyfox) | [booxter](https://github.com/booxter) | [dexhunter](https://github.com/dexhunter) | [DrPaprikaa](https://github.com/DrPaprikaa) | [paulorodriguesxv](https://github.com/paulorodriguesxv) | [stergnator](https://github.com/stergnator) | [Xander Dunn](https://github.com/xanderdunn)\n\n## Disclaimer\n\nThis software is for educational purposes only and is far from any production environment. Do not risk money which you are afraid to lose.\nUse the software at your own risk. The authors assume no responsibility for your trading results.\n',
    'author': 'Marigold',
    'author_email': 'mojmir.vinkler@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Marigold/universal-portfolios',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
