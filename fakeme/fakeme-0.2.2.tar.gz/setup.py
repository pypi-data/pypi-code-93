# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fakeme', 'fakeme.cli', 'fakeme.logic']

package_data = \
{'': ['*'], 'fakeme': ['data/*']}

install_requires = \
['mimesis>=4.0,<5.0',
 'pandas==1.1.5',
 'ply>=3.11,<4.0',
 'pydantic>=1.8.2,<2.0.0',
 'simple-ddl-parser>=0.19.1,<0.20.0']

entry_points = \
{'console_scripts': ['fakeme = fakeme.cli:cli']}

setup_kwargs = {
    'name': 'fakeme',
    'version': '0.2.2',
    'description': 'Relative Data Generator: generate relative tables data, data generator for multi tables that depend on each other',
    'long_description': '\nFakeme\n^^^^^^\n\nData Generator for Chained and Relative Data\n\n\n.. image:: https://img.shields.io/pypi/v/fakeme\n   :target: https://img.shields.io/pypi/v/fakeme\n   :alt: badge1\n \n.. image:: https://img.shields.io/pypi/l/fakeme\n   :target: https://img.shields.io/pypi/l/fakeme\n   :alt: badge2\n \n.. image:: https://img.shields.io/pypi/pyversions/fakeme\n   :target: https://img.shields.io/pypi/pyversions/fakeme\n   :alt: badge3\n \n.. image:: https://github.com/xnuinside/fakeme/actions/workflows/main.yml/badge.svg\n   :target: https://github.com/xnuinside/fakeme/actions/workflows/main.yml/badge.svg\n   :alt: workflow\n\n\nDocumentation in process: https://fakeme.readthedocs.io/en/latest/ \n\nHow to use\n^^^^^^^^^^\n\n.. code-block:: bash\n\n\n       pip install fakeme\n\nCheck examples: https://github.com/xnuinside/fakeme/tree/master/examples\n\nWhat is Fakeme?\n^^^^^^^^^^^^^^^\n\nFakeme is a tools that try to understand your data based on schemas & fields name and generate data relative to expected.\n\nIt create dependencies graph and generate relative data.\n\n**Fakeme** oriented on generation data that depend on values in another tables/datasets.\nData, that knitted together as real.\n\n**Fakeme** can help you if you want to generate several tables, that must contains in columns values, \nthat you will use like key for join.\n\nFor example, *user_data* table has field *user_id* and *users* table contains list of users with column id. \nYou want join it on user_id = id.\n\n**Fakeme** will generate for you 2 tables with same values in those 2 columns. \n\nIt does not matter to have columns with same name you can define dependencies between tables with alias names. \n\nTODO in next releases:\n----------------------\n\n\n#. Add integration with simple-ddl-parser to generated data from different SQL dialects\n#. Add integration with py-models-parser to generated data from different Python models\n#. Fix cases in todo folder\n#. Improve test coverage \n\nWhat you can to do\n^^^^^^^^^^^^^^^^^^\n\n\n#. \n   Define that fields in your datasets must contain similar values\n\n#. \n   You can set up how much values must intersect, for example, you want to emulate data for email validation pipeline -  you have one dataset with *incoming* messages  and you need to find all emails that was not added previously in your *contacts* table.\n\nSo you will have incoming messages table, that contains, for example only 70% of emails that exist in contacts table. \n\n\n#. \n   You can use multiply columns as a key (dependency) in another column, for example, \n   *player_final_report* must contains for each player same values as in other tables, for example, you have *player* table\n   with players details and *in_game_player_activity* with all player activities for some test reasons it\'s critical\n   to you generate *player_final_report* with 1-to-1 data from other 2 tables.\n\n#. \n   Union tables. You can generate tables that contains all rows from another tables. \n\n#. \n   You can define your own generator for fields on Python.\n\n#. \n   You can define your own output format\n\nExamples\n^^^^^^^^\n\nYou can find usage examples in \'fakeme/examples/\' folder.\n\nExample from fakeme/examples/generate_data_related_to_existed_files:\n\n.. code-block:: python\n\n\n       from fakeme import Fakeme\n\n       # to use some existed data you should provide with_data argument -\n       # and put inside list with the paths to the file with data\n\n       # data file must be in same format as .json or csv output of fakeme.\n       # so it must be [{"column_name": value, "column_name2": value2 ..},\n       #   {"column_name" : value, "column_name2": value2 ..}..]\n       # Please check example in countries.json\n\n       cities_schema = [{"name": "name"},\n                        {"name": "country_id"},\n                        {"name": "id"}]\n\n       # all fields are strings - so I don\'t define type, because String will be used as default type for the column\n\n       tables_list = [(\'cities\', cities_schema)]\n\n       Fakeme(\n           tables=tables_list,\n           with_data=[\'countries.json\'],\n           rls={\'cities\': {  # this mean: for table \'cities\'\n               \'country_id\': {  # and column \'country_id\' in table \'cities\'\n                   \'table\': \'countries.json\',   # please take data from data  in countries.json\n                   \'alias\': \'id\',  # with alias name \'id\'\n                   \'matches\': 1  # and I want all values in country_id must be from countries.id column, all.\n               }\n           }},\n           settings={\'row_numbers\': 1300}  # we want to have several cities for each country,\n                                           # so we need to have more rows,\n       ).run()\n\n       # run and you will see a list of cities, that generated with same ids as in countries.json\n\nDocs: https://fakeme.readthedocs.io/en/latest/\n\nChangelog\n---------\n\n**v0.2.2**\n\nFixes:\n^^^^^^\n\n\n#. generate_data_related_to_existed_files example now works well (generation data based on already existing files).\n#. Added integration tests to run examples\n#. Examples are cleaned up, unworking samples moved to \'todo\'\n\n**v0.2.1**\n\n\n#. Now you can define tables as Table class object if it will be more easily for you.\n\n.. code-block:: python\n\n       from fakeme import Table\n\n       Table(name=\'table_name_example\', schema=\'path/to/schema.json\')\n\n       # or \n       user_schema = [{\'name\': \'id\'},\n               {\'name\': \'title\'},\n               {\'name\': \'rights\', \'type\': \'list\', \'alias\': \'right_id\'},\n               {\'name\': \'description\'}]\n       Table(name=\'table_name_example\', schema=user_schema)\n\nsamples it tests: tests/unittests/test_core.py\n\n\n#. Relationships between tables was corrected \n\n**v0.1.0**\n\n\n#. Added code changes to support Python 3.8 and upper (relative to changes in python multiprocessing module)\n#. Added tests runner on GitHub\n#. Autoaliasing was fixed\n#. Added some unit tests\n',
    'author': 'Iuliia Volkova',
    'author_email': 'xnuinside@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/xnuinside/fakeme',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6.2,<4.0',
}


setup(**setup_kwargs)
