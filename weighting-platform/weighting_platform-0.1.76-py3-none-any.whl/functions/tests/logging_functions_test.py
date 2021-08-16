from weighting_platform.functions import logging_functions
from weighting_platform.tests.test_objects import test_sql_shell
import unittest


class LogFuncsTest(unittest.TestCase):
    def test_init_log(self):
        response = logging_functions.init_record_log(test_sql_shell)
        self.assertTrue(type(response) == int)
        return

    def test_mark_record(self):
        response = logging_functions.fix_record_id(test_sql_shell, 482, 3)
        self.assertTrue(response['status'] == 'success')

    def test_fix_event(self):
        response = logging_functions.fix_event(test_sql_shell, 'ТЕСТ')
        print("RESPONSE:", response)

    def test_delete_old_records(self):
        response = logging_functions.delete_old_logs(test_sql_shell)
        print("DELETE RESULT", response)

if __name__ == '__main__':
    unittest.main()