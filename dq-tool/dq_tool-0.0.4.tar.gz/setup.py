# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dq_tool', 'dq_tool.expectation_attributes', 'dq_tool.misc']

package_data = \
{'': ['*']}

install_requires = \
['great-expectations>=0.13.0,<0.14.0', 'sqlalchemy>=1.3.16']

setup_kwargs = {
    'name': 'dq-tool',
    'version': '0.0.4',
    'description': '',
    'long_description': "# dq_tool\nData Quality Tool. Built on top of [Great Expectations](https://greatexpectations.io/)\n\n## Demo\nIf you want to see / show someone DQ Tool in action, use the [Demo Guide](https://www.notion.so/datasentics/Demo-Guide-3af54cfe3344483aa5b2ace4e47c18ef)\n\n## Build\nDQ Tool uses [poetry](https://python-poetry.org/) for dependency management and wheel building. Follow the [installation notes](https://python-poetry.org/docs/basic-usage/), please.\n```sh \npoetry build\n```\nThe wheel will end up in the `dist` folder.\n\n## Databricks Installation\nAs of now, only Databricks runtime 7.x is supported. There have been issues installing the package on 6.x. However if you need to use 6.x get in touch and we'll figure it out. \n\nInstall `dq_tool` from the wheel you built on a cluster or just for a notebook.\n\n## Storing Expectations\nWe support two approaches to storing your expectations: in a Database or in notebooks. These approaches can be combined.\n\n### Expectation Store\nExpectations can be stored in an external database. This database can store expectation definitions and validation results. The validation results can be viewed using our frontend. For the infrastructure setup see our [Deployment Guide](https://www.notion.so/datasentics/Deployment-Guide-703b3a6db9bc4ae594ac113885c21584)\n#### Usage - Expectation Store\nStart with the following code to check that you can connect to the database. Replace the `host`, `port`, `database`, `username` and `password` with the credentials to your database. We highly recommend storing your password in a secure way, in dbutils secrets or Azure Key Vault.\n\nRunning this code also creates the database schema if it's not there yet.\n```python\nfrom dq_tool import DQTool\ndq_tool = DQTool(\n    spark=spark,\n    db_store_connection={\n        'drivername': 'postgresql',\n        'host': 'apostgres.postgres.database.azure.com',\n        'port': '5432',\n        'database': 'postgres',\n        'username': 'postgres@apostgres',\n        'password': dbutils.secrets.get(scope='dq_tool', key='postgres_store_password')\n    }\n)\n```\nSee the [expectation store guide](./docs/expectation_store.md) for details on how to use the store.\n\n### Expectations in Notebooks\nExpectation definitions can also be stored in notebooks as python dicst or code. \n#### Usage - no Store\n```python\nfrom dq_tool import DQTool\ndq_tool = DQTool(spark=spark)\n```\nSee the [notebook expectations guide](.docs/notebook_expectations.md) for details on how to work with expectation definitions in notebooks.\n\n## Guides\nThe following guides can be used both for expectations stored in a database and in a notebook.\n\n### Expectations with Expressions\nSee the [expressions guide](./docs/expressions.md)\n\n### Custom Expectations\nSee the [custom expectations guide](./docs/custom_expectations.md)\n\n### Profiling (beta)\nSee the [profiling guide](./docs/profiling.md)\n",
    'author': 'DataSentics',
    'author_email': 'info@datasentics.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/DataSentics/dq_tool',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
