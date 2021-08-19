import sqlalchemy
from airflow_commons.logger import LOGGER
from sqlalchemy.dialects.mysql import insert


def get_db_engine(
    username: str,
    password: str,
    host: str,
    db_name: str,
):
    """

    :param username: database username
    :param password: database password
    :param host: database host
    :param db_name: database name
    :return:
    """
    db_connection_str = "mysql+pymysql://{username}:{password}@{host}/{dbname}".format(
        username=username, password=password, host=host, dbname=db_name
    )
    engine = sqlalchemy.create_engine(db_connection_str)
    return engine


def get_table_metadata(table_name: str, engine_connection: sqlalchemy.engine.Engine):
    """
    Gets the metadata of given table
    :param table_name: table name to get metadata
    :param engine_connection: database engine connection
    :return: sqlalchemy table.
    """
    return sqlalchemy.Table(
        table_name,
        sqlalchemy.MetaData(),
        autoload=True,
        autoload_with=engine_connection,
    )


def upsert(values: dict, conn, table_name: str):
    """
    :param values: values to write into database
    :param conn: database engine connection
    :param table_name: database table name to write
    :return:
    """
    table_metadata = get_table_metadata(table_name=table_name, engine_connection=conn)
    update_cols = {}
    insert_statement = insert(table_metadata).values(values)
    for col in insert_statement.table.columns:
        col_name = col.name
        if col_name not in table_metadata.primary_key:
            update_cols.update({col_name: getattr(insert_statement.inserted, col_name)})
    upsert_statement = insert_statement.on_duplicate_key_update(**update_cols)
    try:
        conn.execute(upsert_statement)
    except Exception as e:
        LOGGER(str(e), level=1)
        raise
