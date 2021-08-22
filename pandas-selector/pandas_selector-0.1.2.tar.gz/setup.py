# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pandas_selector']

package_data = \
{'': ['*']}

install_requires = \
['pandas>=1,<2']

extras_require = \
{'rtdbuild': ['sphinx>=3.5.0,<4.0.0', 'pydata-sphinx-theme>=0.6.0,<0.7.0']}

setup_kwargs = {
    'name': 'pandas-selector',
    'version': '0.1.2',
    'description': 'Simple, composable column selector for loc[], iloc[], assign() and others.',
    'long_description': 'Pandas Selector\n===============\n\nSimple, composable selectors for ``loc[]``, ``iloc[]``, ``assign()`` and others.\n\n.. image:: https://readthedocs.org/projects/pandas-selector/badge/?version=latest\n  :target: https://pandas-selector.readthedocs.io/en/latest/?badge=latest\n  :alt: Documentation Status\n.. image:: https://github.com/eikevons/pandas-selector/actions/workflows/check.yml/badge.svg\n  :target: https://github.com/eikevons/pandas-selector/actions/workflows/check.yml\n  :alt: Test Status\n\nOverview\n--------\n\n- **Motivation**: Make chaining Pandas operations easier and bring\n  functionality to Pandas similar to Spark\'s `col()\n  <https://spark.apache.org/docs/latest/api/python/reference/api/pyspark.sql.functions.col.html#pyspark.sql.functions.col>`_\n  function or referencing columns in R\'s `dplyr\n  <https://dplyr.tidyverse.org/articles/dplyr.html>`_.\n- **Install** from PyPI with ``pip install\n  pandas-selector``. Pandas versions 1.0+ (``^1.0``) are supported.\n- **Documentation** can be found at `readthedocs\n  <https://pandas-selector.readthedocs.io/en/latest/>`_.\n- **Source code** can be obtained from `GitHub <https://github.com/eikevons/pandas-selector>`_.\n\nExample: Create new column and filter\n-------------------------------------\n\nInstead of writing "traditional" Pandas like this:\n\n.. code-block:: python\n\n    df_in = pd.DataFrame({"x": range(5)})\n    df = df_in.assign(y = df_in.x // 2)\n    df = df.loc[df.y <= 1]\n    df\n    #    x  y\n    # 0  0  0\n    # 1  1  0\n    # 2  2  1\n    # 3  3  1\n\nOne can write:\n\n.. code-block:: python\n\n    from pandas_selector import DF\n    df = (df_in\n          .assign(y = DF.x // 2)\n          .loc[DF.y <= 1]\n         )\n\nThis is especially handy when re-iterating on data frame manipulations\ninteractively, e.g. in a notebook.\n\nBut you can access all methods and attributes of the data frame from the\ncontext:\n\n.. code-block:: python\n\n    df = pd.DataFrame({\n        "X": range(5),\n        "Y": ["1", "a", "c", "D", "e"],\n    })\n    df.loc[DF.y.str.isupper() | DF.y.str.isnumeric()]\n    #    X  y\n    # 0  0  1\n    # 3  3  D\n    df.loc[:, DF.columns.str.isupper()]\n    #    X\n    # 0  0\n    # 1  1\n    # 2  2\n    # 3  3\n    # 4  4\n\nSimilar projects for pandas\n===========================\n\n* `siuba <https://github.com/machow/siuba>`_\n\n  * (+) active\n  * (-) new API to learn\n\n* `pandas-ply <https://github.com/coursera/pandas-ply>`_\n\n  * (-) stale(?), last change 6 years ago\n  * (-) new API to learn\n  * (-) ``Symbol`` / ``pandas_ply.X`` works only with ``ply_*`` functions\n\n* `pandas-select <https://pandas-select.readthedocs.io/en/latest/reference/label_selection.html>`_\n\n  * (+) no explicite ``df`` necessary\n  * (-) new API to learn\n\n* `pandas-selectable <https://github.com/jseabold/pandas-selectable>`_\n\n  * (+) simple ``select`` accessor\n  * (-) usage inside chains clumsy (needs explicite ``df``):\n\n    .. code-block:: python\n\n       ((df\n         .select.A == \'a\')\n         .select.B == \'b\'\n       )\n\n  * (-) hard-coded ``str``, ``dt`` accessor methods\n  * (?) composable?\n\nDevelopment\n===========\n\nDevelopment is containerized with [Docker](https://www.docker.com/) to\nseparte from host systems and improve reproducability. No other\nprerequisites are needed on the host system.\n\n**Recommendation for Windows users:** install `WSL 2\n<https://docs.microsoft.com/en-us/windows/wsl/install-win10>`_ (tested\non Ubuntu 20.04), and for containerized workflows, `Docker\nDesktop <https://www.docker.com/products/docker-desktop>`_ for Windows.\n\nThe **common tasks** are collected in ``Makefile`` (See ``make help`` for a\ncomplete list):\n\n- Run the unit tests: ``make test`` or ``make watch`` for continuously running\n  tests on code-changes.\n- Build the documentation: ``make docs``\n- **TODO**: Update the ``poetry.lock`` file: ``make lock``\n- Add a dependency:\n\n  1. Start a shell in a new container.\n  2. Add dependency with ``poetry add`` in the running container. This will update\n     ``poetry.lock`` automatically::\n\n        # 1. On the host system\n        % make shell\n        # 2. In the container instance:\n        I have no name!@7d0e85b3a303:/app$ poetry add --dev --lock falcon\n\n- Build the development image ``make devimage``\n  (Note: This should be done automatically for the targets.) \n',
    'author': 'Eike von Seggern',
    'author_email': 'eikevons@mailbox.org',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/eikevons/pandas-selector.git',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.6.1,<4.0.0',
}


setup(**setup_kwargs)
