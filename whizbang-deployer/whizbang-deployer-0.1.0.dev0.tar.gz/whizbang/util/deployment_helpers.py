import string
from datetime import datetime
from dateutil.tz import tz
from random import *

# def time_based_unique_id():

def timestamp(string: str):
    utc = tz.tzutc()
    utc_now = datetime.utcnow()
    utc_now = utc_now.replace(tzinfo=utc)

    return f'{utc_now} - {string}'

def sql_db_connection_string(sql_server_name, db_name, user_id, password):
    return f'Server=tcp:{sql_server_name}.database.windows.net,1433;Initial Catalog={db_name};Persist Security Info=False;User ID={user_id};Password={password};MultipleActiveResultSets=False;Encrypt=True;TrustServerCertificate=False;Connection Timeout=30;'

def sql_dw_connection_string(sql_server_name, dw_name, user_id, password):
    return sql_db_connection_string(sql_server_name, dw_name, user_id, password)

def generate_random_password():
    punctuation = '!@#$%^&*()_-+=[{]};:>|./?'
    characters = string.ascii_letters + punctuation + string.digits
    password =  "".join(choice(characters) for x in range(randint(10, 16)))

    # todo: log/save/etc password
    return password
