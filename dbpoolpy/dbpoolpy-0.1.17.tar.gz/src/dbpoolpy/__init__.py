from pymysql import install_as_MySQLdb
install_as_MySQLdb()

from .dbpool import init_pool
from .dbpool import connect_db
from .dbpool import connect_without_exception
from .dbpool import with_connect_db
from .autopool import init_auto_pool
from .autopool import connect_auto_pool
