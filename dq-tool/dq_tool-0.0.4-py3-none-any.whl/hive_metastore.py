"""Hive metastore as a datasource"""


class HiveMetastore:
    """Functions related to the hive metastore - as a datasource"""

    DEFAULT_DATABASE_NAME = 'default'

    @classmethod
    def get_dot_table_name(
        cls,
        database_name: str,
        table_name: str
    ) -> str:
        """Converts whatever it gets to a string like <database>.<table>"""
        database_name, table_name = cls.get_database_table_name(table_name=table_name, database_name=database_name)
        return '{}.{}'.format(database_name, table_name)

    @classmethod
    def get_database_table_name(
        cls,
        database_name: str,
        table_name: str,
        keep_nones: bool = False
    ) -> (str, str):
        """Handles dot table names - table_name can be a string like <database>.<table>.
        Returns a tuple (<database_name>, <table_name>)"""
        if not table_name:
            if not keep_nones:
                raise ValueError("Empty table_name not allowed")
            # don't do anything with database_name, just return it
            return (database_name, table_name)

        splits = table_name.split('.')

        if len(splits) > 2:
            # more dots
            raise ValueError("There're too many dots in your table_name: {}".format(table_name))
        # database.table
        if len(splits) == 2:
            db_name_from_table = splits[0]
            if database_name and db_name_from_table != database_name:
                raise ValueError("There're inconsistent databases in database_name: {} vs the table_name: {}".format(
                    database_name,
                    db_name_from_table
                ))
            return (db_name_from_table, splits[1])  # to keep pylint satisfied
        # splits len is 1
        # just database
        if not database_name and not keep_nones:
            database_name = cls.DEFAULT_DATABASE_NAME
        return (
            database_name,
            splits[0]
        )
