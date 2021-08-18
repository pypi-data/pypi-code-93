from gc_module_cua.main import EventsCatcher
from gc_module_cua.tests.sqlshell_test import sql_shell
from gc_module_cua.tests import settings_test as s


ec = EventsCatcher(sql_shell, s.cm_events_table, s.cm_events_log)
response = ec.try_capture_new_event(event='EXIT', user=1)
print(response)