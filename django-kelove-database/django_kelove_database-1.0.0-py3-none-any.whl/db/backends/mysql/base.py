"""
base.py MySQL database backend for Django.
By IT小强xqitw.cn <mail@xqitw.cn>
At 2/4/21 3:32 PM
"""

from django.db.backends.mysql.base import *

from .schema import DatabaseSchemaEditor as MySqlDatabaseSchemaEditor


class DatabaseWrapper(DatabaseWrapper):
    SchemaEditorClass = MySqlDatabaseSchemaEditor
