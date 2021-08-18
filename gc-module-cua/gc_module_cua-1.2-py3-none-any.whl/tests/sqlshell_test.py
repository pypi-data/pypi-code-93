from wsqluse.wsqluse import Wsqluse
from gc_module_cua.tests import settings_test as s


sql_shell = Wsqluse(s.db_name, s.db_user, s.db_pass, s.db_host)
