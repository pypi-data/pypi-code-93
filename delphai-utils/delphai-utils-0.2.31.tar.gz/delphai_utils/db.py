from delphai_utils.config import get_config
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from multiprocessing import current_process

DB_CONN_BY_PID_AND_DBNAME = {}  # (process id, db_name) -> DB_CONN
db_connection_string = get_config('database.connection_string')
default_database_name = get_config('database.name')
_db_params = {
    'connection_string': db_connection_string,
    'default_db_name': default_database_name,
}


db_client = AsyncIOMotorClient(db_connection_string)
db = db_client[default_database_name or 'main']
db_sync_client = MongoClient(db_connection_string)
db_sync = db_sync_client[default_database_name or 'main']

def get_own_db_connection(db_name: str = None):
  '''
  Creates neq connection to database.
  :param db_name: use this parameter only if DB name differs from _db_params["default_db_name"]
  :return: database connection
  '''
  pid = current_process().pid
  req_db_name = _db_params['default_db_name'] if db_name is None else db_name
  if (pid, req_db_name) in DB_CONN_BY_PID_AND_DBNAME:
      return DB_CONN_BY_PID_AND_DBNAME[(pid, req_db_name)]
  client = MongoClient(_db_params['connection_string'])

  res = client[req_db_name]
  DB_CONN_BY_PID_AND_DBNAME[(pid, req_db_name)] = res
  return res