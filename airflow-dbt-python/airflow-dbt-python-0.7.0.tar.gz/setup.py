# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['airflow_dbt_python',
 'airflow_dbt_python.hooks',
 'airflow_dbt_python.operators']

package_data = \
{'': ['*']}

install_requires = \
['apache-airflow>=1.10.12,<3.0.0', 'dbt-core>=0.19,<0.21']

extras_require = \
{'all': ['dbt-postgres>=0.19,<0.21',
         'dbt-redshift>=0.19,<0.21',
         'dbt-snowflake>=0.19,<0.21',
         'dbt-bigquery>=0.19,<0.21'],
 'amazon': ['apache-airflow-providers-amazon>=2.1.0,<3.0.0'],
 'bigquery': ['dbt-bigquery>=0.19,<0.21'],
 'postgres': ['dbt-postgres>=0.19,<0.21'],
 'redshift': ['dbt-redshift>=0.19,<0.21'],
 'snowflake': ['dbt-snowflake>=0.19,<0.21']}

setup_kwargs = {
    'name': 'airflow-dbt-python',
    'version': '0.7.0',
    'description': 'A dbt operator for Airflow that uses the dbt Python package',
    'long_description': '# airflow-dbt-python\n\n[![](https://img.shields.io/pypi/v/airflow-dbt-python?style=plastic)](https://pypi.org/project/airflow-dbt-python/)\n[![](https://github.com/tomasfarias/airflow-dbt-python/actions/workflows/workflow.yaml/badge.svg)](https://github.com/tomasfarias/airflow-dbt-python/actions)\n\nAn [Airflow](https://airflow.apache.org/) operator to call the `main` function from the [`dbt-core`](https://pypi.org/project/dbt-core/) Python package\n\n# Motivation\n\n## Airflow running in a managed environment\n\nAlthough [`dbt`](https://docs.getdbt.com/) is meant to be installed and used as a CLI, we may not have control of the environment where Airflow is running, disallowing us the option of using `dbt` as a CLI.\n\nThis is exactly what happens when using [Amazon\'s Managed Workflows for Apache Airflow](https://aws.amazon.com/managed-workflows-for-apache-airflow/) or MWAA: although a list of Python requirements can be passed, the CLI cannot be found in the worker\'s PATH.\n\nThere is a workaround which involves using Airflow\'s `BashOperator` and running Python from the command line:\n\n```py\nfrom airflow.operators.bash import BashOperator\n\nBASH_COMMAND = "python -c \'from dbt.main import main; main()\' run"\noperator = BashOperator(\n    task_id="dbt_run",\n    bash_command=BASH_COMMAND,\n)\n```\n\nBut it can get sloppy when appending all potential arguments a `dbt run` command (or other subcommand) can take.\n\nAs you may expect, `airflow-dbt-python` abstracts the complexity of handling CLI arguments by defining an operator for each `dbt` subcommand, and having each operator be defined with attribute for each possible CLI argument.\n\n## An alternative to `airflow-dbt` that works without the dbt CLI\n\nThe existing [`airflow-dbt`](https://pypi.org/project/airflow-dbt/) package, by default, would not work if the `dbt` CLI is not in PATH, which means it would not be usable in MWAA. There is a workaround via the `dbt_bin` argument, which can be set to `"python -c \'from dbt.main import main; main()\' run"`, in similar fashion as the `BashOperator` example. Yet this approach is not without its limitations:\n* `airflow-dbt` works by wrapping the `dbt` CLI, which makes our code dependent on the environment in which it runs.\n* `airflow-dbt` does not support the full range of arguments a command can take. For example, `DbtRunOperator` does not have an attribute for `fail_fast`.\n* `airflow-dbt` does not return anything after the execution, which no information is available for downstream tasks to pull via [XCom](http://airflow.apache.org/docs/apache-airflow/2.1.0/concepts/xcoms.html). An even if it tried to, since it works by wrapping the CLI, it could only attempt to parse the lines printed by `dbt` to STDOUT. On the other hand, `airflow-dbt-python` will try to return the information of a `dbt` result class, as defined in `dbt.contracts.results`, which opens up possibilities for downstream tasks to condition their execution on the result of a `dbt` command.\n\n\n## Avoid installing unnecessary dbt plugins\n\nFinally, `airflow-dbt-python` does not depend on `dbt` but on `dbt-core`. The connectors: `dbt-redshift`, `dbt-postgres`, `dbt-snowflake`, and `dbt-bigquery` are available as installation extras instead of being bundled up by default, which happens when you attempt to install dbt via `python -m pip install dbt`.\n\nThis allows you to easily control what is installed in your environment. One particular example of when this is extremely useful is in the case of the `dbt-snowflake` connector, which depends on [`cryptography`](https://pypi.org/project/cryptography/). This dependency requires the Rust toolchain to run, and this is not supported in a few distributions (like the one MWAA runs on). Even if that\'s not the case, `airflow-dbt-python` results in a lighter installation due to only depending on `dbt-core`.\n\n# Usage\n\nCurrently, the following `dbt` commands are supported:\n\n* `clean`\n* `compile`\n* `debug`\n* `deps`\n* `ls`\n* `parse`\n* `run`\n* `run-operation`\n* `seed`\n* `snapshot`\n* `source` (Not well tested)\n* `test`\n\n## Examples\n\n``` python\nfrom datetime import timedelta\n\nfrom airflow import DAG\nfrom airflow.utils.dates import days_ago\nfrom airflow_dbt_python.operators.dbt import (\n    DbtRunOperator,\n    DbtSeedOperator,\n    DbtTestoperator,\n)\n\nargs = {\n    \'owner\': \'airflow\',\n}\n\nwith DAG(\n    dag_id=\'example_dbt_operator\',\n    default_args=args,\n    schedule_interval=\'0 0 * * *\',\n    start_date=days_ago(2),\n    dagrun_timeout=timedelta(minutes=60),\n    tags=[\'example\', \'example2\'],\n) as dag:\n    dbt_test = DbtTestOperator(\n        task_id="dbt_test",\n        selector="pre-run-tests",\n    )\n\n    dbt_seed = DbtSeedOperator(\n        task_id="dbt_seed",\n        select=["/path/to/first.csv", "/path/to/second.csv"],\n        full_refresh=True,\n    )\n\n    dbt_run = DbtRunOperator(\n        task_id="dbt_run",\n        models=["/path/to/models"],\n        full_refresh=True,\n        fail_fast=True,\n    )\n\n    dbt_test >> dbt_seed >> dbt_run\n```\n\n# Requirements\n\n`airflow-dbt-python` is tested in Python 3.7, 3.8, and 3.9, although it could also support older versions.\n\nOn the Airflow side, we unit test with versions 1.10.12 and upwards, including the latest version 2 release. Regardless, more testing is planned to ensure compatibility with version 2 of Airflow.\n\nFinally, `airflow-dbt-python` requires at least `dbt` version 0.19. Unit tests have verified to pass with version 0.20 after minor changes that should not have major effects anywhere else. Regardless, support for version 0.20 of dbt should be considered experimental.\n\n# Installing\n\n## From PyPI:\n\n``` shell\npip install airflow-dbt-python\n```\n\nAny `dbt` connectors you require may be installed by specifying extras:\n\n``` shell\npip install airflow-dby-python[snowflake,postgres]\n```\n\n## From this repo:\n\nClone the repo:\n``` shell\ngit clone https://github.com/tomasfarias/airflow-dbt-python.git\ncd airflow-dbt-python\n```\n\nWith poetry:\n``` shell\npoetry install\n```\n\nInstall any extras you need, and only those you need:\n``` shell\npoetry install -E postgres -E redshift\n```\n\n# Testing\n\nTests are written using `pytest`, can be located in `test/`, and they can be run locally with `poetry`:\n\n``` shell\npoetry run pytest -vv\n```\n\n# License\n\nThis project is licensed under the MIT license. See ![LICENSE](LICENSE).\n',
    'author': 'Tomás Farías Santana',
    'author_email': 'tomas@tomasfarias.dev',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
