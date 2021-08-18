""" Модуль содержит тесты для модуля start_functions """
import unittest
from wengine.functions import start_functions
from wengine.tests import test_objects


class SFuncsTest(unittest.TestCase):
    """ Класс-тест """

    def test_import_settings(self):
        """ Тестируем импорт настроек, используемых для настройки и запуска
        WEngine """
        response = start_functions.import_db_settings(test_objects.sql_shell)
        print('TEST IMPORT SETTINGS:', response)
        self.assertTrue(type(response) == dict)


if __name__ == '__main__':
    unittest.main()
