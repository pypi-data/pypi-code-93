from sqlalchemy import create_engine
import psycopg2

def create_connection(database: str, user: str, password: str, host: str, port: str, sgbd = 'postgresql'):
    """
    Declare a db connection

    Args:
        database (str): database name
        user (str): user
        password (str): password
        host (str): host
        port (str): port
        sgbd (str, optional): Defaults to 'postgresql'. Change the sgbd string in the db connection-string

    Returns:
        sql alchemy db engine: 
    """ 
    con_string = string_connection(database, user, password, host, port, sgbd = 'postgresql')
    ## Creating db string connection
    return create_engine(con_string)

def string_connection(database: str, user: str, password: str, host: str, port: str, sgbd = 'postgresql'):
    """
    Declare a db connection

    Args:
        database (str): database name
        user (str): user
        password (str): password
        host (str): host
        port (str): port
        sgbd (str, optional): Defaults to 'postgresql'. Change the sgbd string in the db connection-string

    Returns:
        connection string: 
    """    

    ## Creating db string connection
    if sgbd == 'postgresql':
        con_string = f'postgresql://{user}:{password}@{host}:{port}/{database}'
    if sgbd == 'mysql':
        con_string = f'mysql+pymysql://{user}:{password}@{host}:{port}/{database}'
    if sgbd == 'redshift':
        con_string = f'redshift+psycopg2://{user}:{password}@{host}:{port}/{database}'
    return con_string