# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['whizbang',
 'whizbang.config',
 'whizbang.container',
 'whizbang.core',
 'whizbang.data',
 'whizbang.data.databricks',
 'whizbang.data.pyodbc',
 'whizbang.domain.commandline',
 'whizbang.domain.handler',
 'whizbang.domain.manager',
 'whizbang.domain.manager.az',
 'whizbang.domain.manager.bicep',
 'whizbang.domain.manager.databricks',
 'whizbang.domain.manager.pyodbc',
 'whizbang.domain.menu',
 'whizbang.domain.models',
 'whizbang.domain.models.active_directory',
 'whizbang.domain.models.commandline',
 'whizbang.domain.models.databricks',
 'whizbang.domain.models.keyvault',
 'whizbang.domain.models.menu',
 'whizbang.domain.models.sql',
 'whizbang.domain.models.storage',
 'whizbang.domain.repository',
 'whizbang.domain.repository.az',
 'whizbang.domain.repository.databricks',
 'whizbang.domain.repository.sql_server',
 'whizbang.domain.shared_types',
 'whizbang.domain.solution',
 'whizbang.domain.workflow',
 'whizbang.domain.workflow.bicep',
 'whizbang.domain.workflow.databricks',
 'whizbang.domain.workflow.datalake',
 'whizbang.notes',
 'whizbang.solutions.cortex_accelerator',
 'whizbang.solutions.cortex_accelerator.Databricks.Notebooks.DWH',
 'whizbang.solutions.cortex_accelerator.Databricks.Notebooks.DataEngineering',
 'whizbang.solutions.cortex_accelerator.Databricks.Notebooks.DataEngineering.ClassModules',
 'whizbang.util']

package_data = \
{'': ['*'],
 'whizbang': ['reference/*',
              'solutions/*',
              'solutions/cortex_accelerator/Databricks/*',
              'solutions/cortex_accelerator/Databricks/Clusters/*',
              'solutions/cortex_accelerator/Databricks/Jobs/*',
              'solutions/cortex_accelerator/Databricks/Libraries/*',
              'solutions/cortex_accelerator/Databricks/Notebooks/*',
              'solutions/cortex_accelerator/Databricks/Pools/*',
              'solutions/cortex_accelerator/Datalake/*',
              'solutions/cortex_accelerator/sql/*']}

install_requires = \
['az.cli>=0.5,<0.6',
 'databricks-cli>=0.15.0,<0.16.0',
 'dependency-injector>=4.35.2,<5.0.0',
 'pyodbc>=4.0.32,<5.0.0',
 'pytest>=6.2.4,<7.0.0',
 'sqlparse>=0.4.1,<0.5.0']

setup_kwargs = {
    'name': 'whizbang-deployer',
    'version': '0.1.0.dev0',
    'description': 'Whizbang Deployer - An all-in-one Azure deployment solution',
    'long_description': 'whizbang-deployer readme placeholder',
    'author': 'Brian Aiken',
    'author_email': 'baiken@hitachisolutions.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/hitachisolutionsamerica/whizbang-deployer',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
