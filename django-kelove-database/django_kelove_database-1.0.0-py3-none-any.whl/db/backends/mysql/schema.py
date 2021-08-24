"""
schema.py MySQL database backend for Django.
By IT小强xqitw.cn <mail@xqitw.cn>
At 2/4/21 3:32 PM
"""

from inspect import isfunction

from django.db.backends.mysql.schema import DatabaseSchemaEditor as MySqlDatabaseSchemaEditor

from django.conf import settings


class DatabaseSchemaEditor(MySqlDatabaseSchemaEditor):

    def prepare_default(self, value):
        return super().prepare_default(value)

    def column_sql(self, model, field, include_default=False):
        """
        重写 字段sql生成方法
        :param model:
        :param field:
        :param include_default:
        :return:
        """

        # 解析 include_default
        include_default = self._get_include_default_fun(model, field, include_default)

        # 生成sql
        sql, params = super().column_sql(model, field, include_default)
        sql, params = self._get_column_sql_params(field, sql, params)

        return sql, params

    def table_sql(self, model):
        """
        重写表sql生成方法
        :param model:
        :return:
        """

        sql, params = super().table_sql(model)
        comment = model._meta.verbose_name
        if comment:
            sql += self._get_sql_comment(comment)

        return sql, params

    def _get_include_default_fun(self, model, field, include_default=False):
        # 字段默认值是否写入到sql语句中处理，可在settings.py中配置
        include_default_fun = self.connection.settings_dict.get(
            'INCLUDE_DEFAULT',
            getattr(settings, 'DATABASE_INCLUDE_DEFAULT', False)
        )

        if isinstance(include_default_fun, bool):
            include_default = include_default_fun
        elif isfunction(include_default_fun):
            include_default = include_default_fun(model, field, include_default, self.connection)
        else:
            include_default = bool(include_default_fun)
        return include_default

    def _get_column_sql_params(self, field, sql, params):
        if not isinstance(sql, str):
            return sql, params

        # 写入字段注释
        comment = ''
        if field.help_text:
            comment = field.help_text
        elif field.verbose_name:
            comment = field.verbose_name
        sql += self._get_sql_comment(comment)

        return sql, params

    def _get_sql_comment(self, comment: str) -> str:
        comment = self._get_safe_sql_str(comment)
        return f" COMMENT '{comment}'"

    @classmethod
    def _get_safe_sql_str(cls, sql_str: str) -> str:
        """
        特殊字符转义处理
        :param sql_str:
        :return:
        """
        sql_str = sql_str.replace(r"'", r"\'").replace('%', '%%')
        return sql_str
