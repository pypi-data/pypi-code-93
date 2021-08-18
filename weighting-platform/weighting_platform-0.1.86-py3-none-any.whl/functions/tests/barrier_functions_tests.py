""" Модуль содержит тесты основного класса"""
import unittest
from weighting_platform.functions import barrier_functions
from weighting_platform.tests import test_objects
from weighting_platform.functions import general_functions


class FunctionsTest(unittest.TestCase):
    """ Тесты функций  """
    def __init__(self, *args, **kwargs):
        """ Инициируем многоиспользуемые объекты"""
        super(FunctionsTest, self).__init__(*args, **kwargs)
        self.qsb = test_objects.test_qsb

    def test_form_gate_name(self):
        """ Тестируем корректность формирования имени шлагбаума для QSB"""
        response = general_functions.form_point_name('external', 'GATE')
        response_must = 'EXTERNAL_GATE'
        self.assertEqual(response, response_must)

    def test_open_barrier(self):
        """ Протестировать открытие шлагбаумов"""
        course = 'external'
        barrier_functions.open_barrier(self.qsb, course)
        barrier_name = general_functions.form_point_name(course, 'GATE')
        response = self.qsb.get_point_state(barrier_name)
        response_must = self.qsb.get_unlock_state_str()
        self.assertEqual(response, response_must)

    def test_close_barrier(self):
        """ Протестировать открытие шлагбаумов"""
        course = 'internal'
        barrier_functions.close_barrier(self.qsb, course)
        barrier_name = general_functions.form_point_name(course, 'GATE')
        response = self.qsb.get_point_state(barrier_name)
        response_must = self.qsb.get_lock_state_str()
        self.assertEqual(response, response_must)

    def test_barrier_status(self):
        barrier_functions.barrier_status('external', 'opening')

if __name__ == '__main__':
    unittest.main()
