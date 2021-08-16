# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['data_check', 'data_check.test_type']

package_data = \
{'': ['*']}

install_requires = \
['Jinja2>=2.11.3,<3.0.0',
 'SQLAlchemy>=1.4,<2.0',
 'click>=7.1.2,<8.0.0',
 'colorama>=0.4.4,<0.5.0',
 'importlib-metadata>=3.4.0,<4.0.0',
 'numpy>=1.19.5,<2.0.0',
 'pandas>=1.1.5,<2.0.0',
 'python-dateutil>=2.8.2,<3.0.0',
 'pyyaml>=5.3.1,<6.0.0']

extras_require = \
{'mssql': ['pyodbc>=4.0.30,<5.0.0'],
 'mysql': ['pymysql[rsa]'],
 'oracle': ['cx_Oracle>=8.1.0,<9.0.0'],
 'postgres': ['psycopg2-binary>=2.8.6,<3.0.0']}

entry_points = \
{'console_scripts': ['data_check = data_check.__main__:main']}

setup_kwargs = {
    'name': 'data-check',
    'version': '0.7.0',
    'description': 'simple data validation',
    'long_description': '# data_check\n\ndata_check is a simple data validation tool. In its most basic form it will execute SQL queries and compare the results against CSV files. But there are more advanced features:\n\n## Features\n\n* [CSV checks](#csv-checks): compare SQL queries against CSV files\n* multiple environments (databases) in the configuration file\n* populate tables from CSV files\n* execute any SQL files on a database\n* more complex [pipelines](#pipelines)\n* run any script/command (via pipelines)\n\n## Database support\n\ndata_check should work with any database that works with [SQLAlchemy](https://docs.sqlalchemy.org/en/14/dialects/). Currently data_check is tested against PostgreSQL, MySQL, SQLite, Oracle and Microsoft SQL Server.\n\n## Quickstart\n\nYou need Python 3.6.2 or above to run data_check. The easiest way to install data_check is via [pipx](https://github.com/pipxproject/pipx):\n\n`pipx install data-check`\n\nThe data_check Git repository is also a sample data_check project. Clone the repository, switch to the folder and run data_check:\n\n```\ngit clone git@github.com:andrjas/data_check.git\ncd data_check\ndata_check\n```\n\nThis will run the tests in the _checks_ folder using the default connection as set in data_check.yml.\n\nSee the [documentation](https://andrjas.github.io/data_check) how to install data_check in different environments with additional database drivers and other usages of data_check.\n\n## Project layout\n\ndata_check has a simple layout for projects: a single configuration file and a folder with the test files. You can also organize the test files in subfolders.\n\n    data_check.yml    # The configuration file\n    checks/           # Default folder for data tests\n        some_test.sql # SQL file with the query to run against the database\n        some_test.csv # CSV file with the expected result\n        subfolder/    # Tests can be nested in subfolders\n\n## CSV checks\n\nThis is the default mode when running data_check. data_check expects a SQL file and a CSV file. The SQL file will be executed against the database and the result is compared with the CSV file. If they match, the test is passed, otherwise it fails.\n\n## Pipelines\n\nIf data_check finds a file named _data\\_check\\_pipeline.yml_ in a folder, it will treat this folder as a pipeline check. Instead of running [CSV checks](#csv-checks) it will execute the steps in the YAML file.\n\nExample project with a pipeline:\n\n    data_check.yml\n    checks/\n        some_test.sql                # this test will run in parallel to the pipeline test\n        some_test.csv\n        sample_pipeline/\n            data_check_pipeline.yml  # configuration for the pipeline\n            data/\n                my_schema.some_table.csv       # data for a table\n            data2/\n                some_data.csv        # other data\n            some_checks/             # folder with CSV checks\n                check1.sql\n                check1.csl\n                ...\n            run_this.sql             # a SQL file that will be executed\n            cleanup.sql\n        other_pipeline/              # you can have multiple pipelines that will run in parallel\n            data_check_pipeline.yml\n            ...\n\nThe file _sample\\_pipeline/data\\_check\\_pipeline.yml_ can look like this:\n\n```yaml\nsteps:\n    # this will truncate the table my_schema.some_table and load it with the data from data/my_schema.some_table.csv\n    - load_tables: data\n    # this will execute the SQL statement in run_this.sql\n    - sql_file: run_this.sql\n    # this will append the data from data2/some_data.csv to my_schema.other_table\n    - load:\n        file: data2/some_data.csv\n        table: my_schema.other_table\n        load_mode: append\n    # this will run a python script and pass the connection name\n    - cmd: "python3 /path/to/my_pipeline.py --connection {{CONNECTION}}"\n    # this will run the CSV checks in the some_checks folder\n    - check: some_checks\n```\n\nPipeline checks and simple CSV checks can coexist in a project.\n\n## Documentation\n\nSee the [documentation](https://andrjas.github.io/data_check) how to setup data_check, how to create a new project and more options.\n',
    'author': 'Andreas Rjasanow',
    'author_email': 'andrjas@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://andrjas.github.io/data_check/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.6.2,<4.0.0',
}


setup(**setup_kwargs)
