# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['sparkmon']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.0.1,<9.0.0',
 'data-science-types',
 'ipython',
 'matplotlib',
 'pandas',
 'pandas-stubs',
 'pathlib',
 'psutil',
 'pyspark',
 'urlpath']

extras_require = \
{'mlflow': ['mlflow']}

entry_points = \
{'console_scripts': ['sparkmon = sparkmon.__main__:main']}

setup_kwargs = {
    'name': 'sparkmon',
    'version': '0.0.6',
    'description': 'sparkmon',
    'long_description': "sparkmon\n========\n\n|PyPI| |Python Version| |License|\n\n|Read the Docs| |Tests| |Codecov|\n\n|pre-commit| |Black|\n\n.. |PyPI| image:: https://img.shields.io/pypi/v/sparkmon.svg\n   :target: https://pypi.org/project/sparkmon/\n   :alt: PyPI\n.. |Python Version| image:: https://img.shields.io/pypi/pyversions/sparkmon\n   :target: https://pypi.org/project/sparkmon\n   :alt: Python Version\n.. |License| image:: https://img.shields.io/pypi/l/sparkmon\n   :target: https://opensource.org/licenses/MIT\n   :alt: License\n.. |Read the Docs| image:: https://img.shields.io/readthedocs/sparkmon/latest.svg?label=Read%20the%20Docs\n   :target: https://sparkmon.readthedocs.io/\n   :alt: Read the documentation at https://sparkmon.readthedocs.io/\n.. |Tests| image:: https://github.com/stephanecollot/sparkmon/workflows/Tests/badge.svg\n   :target: https://github.com/stephanecollot/sparkmon/actions?workflow=Tests\n   :alt: Tests\n.. |Codecov| image:: https://codecov.io/gh/stephanecollot/sparkmon/branch/master/graph/badge.svg\n   :target: https://codecov.io/gh/stephanecollot/sparkmon\n   :alt: Codecov\n.. |pre-commit| image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white\n   :target: https://github.com/pre-commit/pre-commit\n   :alt: pre-commit\n.. |Black| image:: https://img.shields.io/badge/code%20style-black-000000.svg\n   :target: https://github.com/psf/black\n   :alt: Black\n\nDescription\n-----------\n\n``sparkmon`` is a Python package to monitor Spark applications. You can see it as an advanced Spark UI, that keep track all of `Spark REST API <SparkREST_>`_ metrics over time. It is specifically useful to do memory profiling.\n\n\nFeatures\n--------\n\nMonitoring plot example:\n\n.. image:: docs/_static/monitoring-plot-example.png\n\n* Log the executors metrics\n* Plot monitoring, display in a notebook, or export to a file\n* Can monitor remote Spark application\n* Can run directly in your PySpark application, or run in a notebook, or via the command-line interface\n* Log to mlflow\n\n\nRequirements\n------------\n\n* Python\n* Spark\n* mlflow (optional)\n\n\nInstallation\n------------\n\nYou can install *sparkmon* via pip_ from PyPI_:\n\n.. code:: console\n\n   $ pip install sparkmon\n   $ pip install sparkmon[mlflow]\n\n\nUsage\n-----\n\n.. code-block:: python\n\n   import sparkmon\n\n   # Create an app connection\n   # via a Spark session\n   application = sparkmon.create_application_from_spark(spark)\n   # or via a remote Spark web UI link\n   application = sparkmon.create_application_from_link(index=0, web_url='http://localhost:4040')\n\n   # Create and start the monitoring process\n   mon = sparkmon.SparkMon(application, period=5, callbacks=[\n       sparkmon.callbacks.plot_to_image,\n       sparkmon.callbacks.log_to_mlflow,\n   ])\n   mon.start()\n\n   # Stop monitoring\n   mon.stop()\n\nYou can also use it from a notebook: `Notebook Example <Example_>`_\n\nThere is also a command-line interface, see  `Command-line Reference <Usage_>`_ for details.\n\n\nHow does it work?\n-----------------\n\n``SparkMon`` is running in the background a Python thread that is querying Spark web UI API and logging all the executors information over time.\n\nThe ``callbacks`` list parameters allows you to define what do after each update, like exporting executors historical info to a csv, or plotting to a file, or to your notebook.\n\n\nContributing\n------------\n\nContributions are very welcome.\nTo learn more, see the `Contributor Guide`_.\n\n\nLicense\n-------\n\nDistributed under the terms of the `MIT license`_,\n*sparkmon* is free and open source software.\n\n\nIssues\n------\n\nIf you encounter any problems,\nplease `file an issue`_ along with a detailed description.\n\n\nCredits\n-------\n\nThis project was generated from `@cjolowicz`_'s `Hypermodern Python Cookiecutter`_ template.\n\n.. _@cjolowicz: https://github.com/cjolowicz\n.. _Cookiecutter: https://github.com/audreyr/cookiecutter\n.. _MIT license: https://opensource.org/licenses/MIT\n.. _PyPI: https://pypi.org/\n.. _Hypermodern Python Cookiecutter: https://github.com/cjolowicz/cookiecutter-hypermodern-python\n.. _file an issue: https://github.com/stephanecollot/sparkmon/issues\n.. _pip: https://pip.pypa.io/\n.. github-only\n.. _Contributor Guide: CONTRIBUTING.rst\n.. _Usage: https://sparkmon.readthedocs.io/en/latest/usage.html\n.. _Example: https://sparkmon.readthedocs.io/en/latest/example.html\n.. _SparkREST: https://spark.apache.org/docs/latest/monitoring.html#rest-api\n",
    'author': 'Stephane Collot',
    'author_email': 'stephane.collot@ing.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/stephanecollot/sparkmon',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.6.1,<4.0.0',
}


setup(**setup_kwargs)
