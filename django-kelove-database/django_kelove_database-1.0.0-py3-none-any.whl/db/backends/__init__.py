"""
__init__.py
By IT小强xqitw.cn <mail@xqitw.cn>
At 2/4/21 3:31 PM
"""

from importlib import import_module

from django.conf import settings
from django.db import DEFAULT_DB_ALIAS


def get_database_doc_obj(db_alias: str = DEFAULT_DB_ALIAS):
    db_backend = settings.DATABASES[db_alias]['ENGINE']
    db_backend_doc = f'{db_backend}.doc.Doc'
    dot = db_backend_doc.rindex('.')
    module, name = db_backend_doc[:dot], db_backend_doc[dot + 1:]
    return getattr(import_module(module), name)


def database_doc_reader(request, doc_title='数据库在线文档', apps_list=None, db_alias: str = DEFAULT_DB_ALIAS, **kwargs):
    """

    :param request:
    :param doc_title:
    :param apps_list:
    :param db_alias:
    :param kwargs:
    :return:
    """
    doc_obj = get_database_doc_obj(db_alias=db_alias)
    return doc_obj().render(request=request, doc_title=doc_title, apps_list=apps_list, **kwargs)
