# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['table_meta']

package_data = \
{'': ['*']}

install_requires = \
['pydantic>=1.8.2,<2.0.0']

setup_kwargs = {
    'name': 'table-meta',
    'version': '0.1.0',
    'description': 'Universal class that created to be a middleware, universal mapping for data from different parsers - simple-ddl-parser and py-models-parser',
    'long_description': '\nTable Meta\n^^^^^^^^^^\n\nIt\'s a universal class that created to be a middleware, universal mapping for data from different parsers - simple-ddl-parser and py-models-parser.\n\nBased on this middleware 2 libraries are worked - omymodels & fakeme. \n\nIt\'s allow create 1 adapter for different inputs and produce output only on one standard - easy to maintain ad add different output variants.\n\nAll classes - Pydantic classes, so you can do with them anything that you can with Pydantic classes.\n\nLibrary contains 2 different classes - TableMeta - main class to convert input relative to models or tables. Second - Type, for Enum types data.\n\nHow it use\n^^^^^^^^^^\n\nInstall\n-------\n\n.. code-block:: bash\n\n\n       pip install table-meta\n\nUsage\n-----\n\n.. code-block:: python\n\n\n   from table_meta import TableMeta\n\n   data = {your_table_definition}\n\n   table_data = TableMeta(**data)\n\nConvert simple-ddl-parser input to TableMeta\n^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n\nSimple-ddl-parser: https://github.com/xnuinside/simple-ddl-parser\n\nPay attention that TableMeta expected data from simple-ddl-parser , that created with flag \'group_by_type=True\'\nExample: result = DDLParser(ddl).run(group_by_type=True, output_mode="bigquery")\n\nTo convert simple-ddl-parser output to TableMeta - use method: ddl_to_meta()\n\nUsage example:\n\n.. code-block:: python\n\n\n       from simple_ddl_parser import DDLParser\n       from table_meta import ddl_to_meta\n\n       ddl = "your ddl"\n       parser_result = DDLParser(ddl).run(group_by_type=True, output_mode="bigquery")\n       data = ddl_to_meta(parser_result)\n\n       # ddl_to_meta returns Dict with 2 keys {"tables": [], "types": []} inside lists you will have Table Meta a models\n\n       print(data)\n\nConvert py-model-parser input to TableMeta\n^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n\nPy-models-parser: https://github.com/xnuinside/py-models-parser\n\nUsage example:\n\n.. code-block:: python\n\n\n       from py_models_parser import parse\n       from table_meta import models_to_meta\n\n       model_from = "your python models, supported by parser"\n       result = parse(model_from)\n       data = models_to_meta(result)\n\n       # models_to_meta returns Dict with 2 keys {"tables": [], "types": []} inside lists you will have a Table Meta models\n\n       print(data)\n\nChangelog\n---------\n\n**v0.1.0**\n\n\n#. Table Meta moved from O!MyModels to separate library. To make it re-usebale in fakeme library.\n',
    'author': 'Iuliia Volkova',
    'author_email': 'xnuinside@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/xnuinside/table-meta',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6.2,<4.0',
}


setup(**setup_kwargs)
