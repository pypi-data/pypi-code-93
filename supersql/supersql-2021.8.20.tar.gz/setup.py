# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['supersql',
 'supersql.connection',
 'supersql.constants',
 'supersql.core',
 'supersql.datatypes',
 'supersql.engines',
 'supersql.errors',
 'supersql.errors.postgres',
 'supersql.functions',
 'supersql.utils',
 'supersql.utils.pg']

package_data = \
{'': ['*']}

entry_points = \
{'console_scripts': ['supersql = supersql:main']}

setup_kwargs = {
    'name': 'supersql',
    'version': '2021.8.20',
    'description': 'Thin wrapper on top of SQL that enables you write SQL code in python easily',
    'long_description': 'Supersql Library\n================\nThere are many great database tools for python (i.e. databases, SQLAlchemy, PeeWee etc.) - **but there is no Python tool for databases.**\n\nIn addition you might have come to the same realisation and thinking the following:\n\n1. But we don\'t want to use an ORM\n\n2. Why can\'t we get a low level pythonic, powerful SQL api with with semantic interaction primitives\n\n3. Async and Sync support should be supported\n\nSupersql checks all those boxes and more. It is a python superset of SQL - allowing you leverage the full power of python to\nwrite advanced SQL queries.\n\n&nbsp;\n\n**Tutorial**: [Open Documentation](https://rayattack.github.io/supersql/)\n\n**Requirements**: Python 3.6+\n\n&nbsp;\n\n\n### NOTE: Still Very Much In Development\n\n```sql\nSELECT * FROM customers ORDER BY last_name ASC LIMIT 5\n```\n\n\n```py\n# query.SELECT(\'*\') is the same as query.SELECT() or query.SELECT(customers)\nquery.SELECT().FROM(customers).ORDER_BY(-customers.last_name).LIMIT(5)\n```\n\n&nbsp;\n\n## Why?\nLet\'s be honest:\n\n1. Writing sql templates using string formatting is really painful.\n2. Sometimes an ORM is not what you need, and whilst the new\n`f strings` in python solve a lot of problems, complex SQL templating is not of\nthem.\n\n3. Supersql makes it super simple to connect to and start querying a database in python.\n\n&nbsp;\n\nLet the code do the explanation:\n```py\n\nfrom supersql import Query\n\n\nquery = Query(\'postgres://user:password@hostname:5432/database\')\n\n\n# Without table schema discovery/reflection i.e. using strings -- NOT OPTIMAL\nresults = query.SELECT(\n        \'first_name\', \'last_name\', \'email\'\n    ).FROM(\n        \'employees\'\n    ).WHERE(\'email = someone@example.com\').execute()\n\nfor result in results:\n    print(result)\n\n\n# reflect table schema and fields into a python object for easy querying\nemps = query.database.table(\'employees\')\n\nrecords = query.SELECT(\n        emps.first_name, emps.last_name, emps.email\n    ).FROM(\n        emps\n    ).WHERE(emps.email == \'someone@example.com\').execute()\n```\n\n&nbsp;\n\nWhat about support for Code First flows? Also supported using Table objects\n```py\nfrom supersql import Table, Varchar, Date, Smallint\n\nclass Employee(Table):\n    """\n    SuperSQL is not an ORM. Table only helps you avoid magic\n    literals in your code. SuperSQL is not an ORM\n    """\n    __pk__ = (\'email\', \'identifier\')\n\n    identifier = Varchar()\n    email = Varchar(required=True, unique=None, length=25)\n    age = Smallint()\n    first_name = String(required=True)\n    last_name = String(25)\n    created_on = Date()\n\n\n# Now lets try again\nemp = Employee()\nresults = query.SELECT(\n    emp.first_name, emp.last_name, emp.email\n).FROM(emp).WHERE(\n    emp.email == \'someone@example.com\'\n).execute()\n```\n\n\n&nbsp;\n\n\n**Note**\n---\n**Supersql is not an ORM so there is no magic Table.save() Table.find() features nor will they ever be supported.**\nThe `Table` class is provided only to help with magic literal elimination from your codebase i.e. a query helper and nothing more.\n\n---\n',
    'author': 'Raymond Ortserga',
    'author_email': 'codesage@live.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/rayattack/supersql',
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
