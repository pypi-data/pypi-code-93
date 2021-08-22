
from typing import Union, Dict

from MySQLdb import connect, MySQLError
from MySQLdb._exceptions import OperationalError
from MySQLdb.cursors import DictCursor

class Connection(object):
    HOST_KEY = 'host'
    NAME_KEY = 'name'
    DB_KEY = 'db'

    def __init__(self, host, user, passwd=None, db=None, ssl_key=None, ssl_cert=None, name=None):
        self.data = dict(
            host=host,
            user=user,
            passwd=passwd,
            db=db,
            ssl=dict(key=ssl_key, cert=ssl_cert),
            name=name,
            cursorclass=DictCursor
        )

    def __enter__(self):
        try:
            self.instance = connect(**{k: v for k, v in self.data.items() if v and k != Connection.NAME_KEY})

        except OperationalError:
            raise MySQLError(
                f'Connection to {self.data.get(Connection.NAME_KEY) if Connection.NAME_KEY in self.data else self.data.get(Connection.HOST_KEY)} Failed'
            ) 
        
        return self.instance
      
    def __exit__(self, exc_type, exc_value, exc_traceback):
        try:
            self.instance.close() 
            
        except AttributeError:
            pass
    
    @property
    def db(self):
        return self.data.get(Connection.DB_KEY)

    @property
    def name(self):
        return self.data.get(Connection.NAME_KEY, self.data.get(Connection.HOST_KEY))

def connections(conns: Dict[str, Connection] = {}):
    ''' 
        Dict of pre existing Connection Objects (name: connection)
        Setup new connections, returns all available
    '''
    try:
        connections.__CONNECTIONS.update(conns)

    except AttributeError:
        connections.__CONNECTIONS = {**conns}

    if not connections.__CONNECTIONS:
        return {None: None}

    return connections.__CONNECTIONS

def __get_known_connection(connection: Union[Connection, str]):
    # If no connection is provided, grab first available
    if not connection:
        connection = list(connections().keys())[0]

    # Provided connection is not a Connection, is it a key?
    if not isinstance(connection, Connection):
        connection = connections().get(str(connection), connection)
    
    # No connection could be found
    if not isinstance(connection, Connection):
        raise KeyError(f'Unknown Connection', connection)

    return connection

        