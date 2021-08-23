"""
Модуль тестирования класса Slush
"""

import unittest
from slush_list import Students
from main import get_stud
from main import get_repos
from main import groups_dir


class TestFunctions(unittest.TestCase):
    """Класс тестирования методов класса Students"""

    def setUp(self):
        """Начальные параметры"""

        self.test_slush = Students(year="2018", number="3")
        self.test_slush.read_slush("./example.txt")

        self.test_slush2 = Students(year="2017", number="3")
        self.test_slush2.read_slush("./example2.txt")

    def test_read_list(self):
        """Тестирование чтения списка"""

        self.assertTrue(self.test_slush.read_slush("./example.txt"))

    def test_load_list(self):
        """Тестирование загрузки списка"""

        self.assertTrue(self.test_slush.load_slush())

    def test_relogin(self):
        """Тестирование функции замены login слушателя"""

        self.test_slush.load_slush()

        change = ['nazar_lex', 'nazarov']

        self.assertTrue(self.test_slush.relogin(change[0], change[1]))

    def test_rename(self):
        """Тестирование функции замены fullname слушателя"""

        self.test_slush.load_slush()

        change = ['nazar_lex', '2018-3-21-nazarov']

        self.assertTrue(self.test_slush.rename(change[0], change[1]))

    def test_check(self):
        """Тестирование функции проверки fullname слушателей"""

        self.test_slush.load_slush()

        self.assertTrue(self.test_slush.check_name("2018-3-20-naz"))

    def test_get_stud(self):
        """Тестирование функции поиска слушателя по шаблону"""

        groups_dir[self.test_slush.load_slush()] = self.test_slush
        self.assertTrue(get_stud("2018-3-20-naz"))

    def test_get_repos(self):
        """Тестирование функции получения списка репозиториев"""

        groups_dir[self.test_slush.load_slush()] = self.test_slush
        self.assertTrue(get_repos("2018-3", "timp", '-r'))
        self.assertTrue(get_repos("2018-3", "timp/roi", '-g'))


class TestFunctionsRaises(unittest.TestCase):
    """Класс тестирования исключений в методах класса Students"""

    def setUp(self):
        """Начальные параметры"""

        self.test_slush_raises = Students(year="2018", number="3")
        self.test_slush_raises.read_slush("./example.txt")

    def test_raise_load(self):
        """Тестирование исключения в функции загрузки списка"""

        self.assertRaises(FileNotFoundError, self.test_slush_raises.read_slush, "123.txt")

    def test_raise_relog(self):
        """Тестирование исключения в функции изменения login слушателя"""

        self.assertRaises(ValueError, self.test_slush_raises.relogin, "123", "nazarov")

    def test_raise_rename(self):
        """Тестирование исключения в функции изменения fullname слушателя"""

        self.assertRaises(Exception, self.test_slush_raises.rename, "123", "2018-3-21-nazarov")


if __name__ == '__main__':
    unittest.main()
