from gc_module_cua import functions
from gc_module_cua.tests.sqlshell_test import sql_shell
import unittest
import datetime


class FunctionsTest(unittest.TestCase):
    def test_capture_event(self):
        response = functions.insert_data_db(sql_shell, 'cm_events_log',
                                            1, datetime.datetime.now())
        print('RESPONSE:', response)


if __name__ == '__main__':
    unittest.main()