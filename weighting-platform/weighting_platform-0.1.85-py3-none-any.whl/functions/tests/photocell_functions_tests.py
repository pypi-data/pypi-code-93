import unittest
from weighting_platform.functions import photocell_functions
from weighting_platform.tests.test_objects import test_qsb
import threading
import time


class PhotocellTest(unittest.TestCase):
    """ Класс для проведения тестов с фотоэлементами """
    def photo_tracer_test_mask(self, photocell_name='INTERNAL_PHOTOCELL',
                               spare_time=4, block_after=3, normal_after=3,
                               thread_must_dead=True, block_after_spare=None,
                               unblock_after_spare=None, add_time=1):
        """
        :param photocell_name: Название фотоэлемента
        :param spare_time: Время ожидания возможного повтороного блока после деблока
        :param block_after: Время блокирования после начала слежения
        :param normal_after: Время деблока после блока
        :param thread_must_dead: Должен ли поток слежения помереть
        :param block_after_spare: (Опционально) Блок после нормализации деблока
        :param unblock_after_spare:(Опционально) Деблок после блока после деблока
        :param add_time: Добавоченое ремя ожидания смерти потока слежения
        :return:
        """
        trace_thread = threading.Thread(target=photocell_functions.photocell_tracer,
                         args=(test_qsb, photocell_name, spare_time))
        trace_thread.start()
        time.sleep(block_after)
        test_qsb.lock_point(photocell_name)
        time.sleep(normal_after)
        test_qsb.normal_point(photocell_name)
        if block_after_spare:
            time.sleep(block_after_spare)
            test_qsb.lock_point(photocell_name)
            if unblock_after_spare:
                time.sleep(unblock_after_spare)
                test_qsb.normal_point(photocell_name)
        time.sleep(spare_time + add_time)
        self.assertEqual(trace_thread.is_alive(), not thread_must_dead)

    def stest_normal_tracing(self):
        """ Обычный сценарий слежения (блок-нормализация) """
        self.photo_tracer_test_mask('INTERNAL_PHOTOCELL', spare_time=4,
                                    block_after=3, normal_after=3)

    def test_block_tracing(self):
        """ Сценарий, когда после блока и деблока, в течение spare_time образовался
        блок, который затем был снят. """
        self.photo_tracer_test_mask('EXTERNAL_PHOTOCELL', spare_time=4, block_after=3,
                                    normal_after=3, block_after_spare=2,
                                    thread_must_dead=True, unblock_after_spare=2)

    def test_block_unblock_tracing(self):
        """ Сценарий, когда после блока и деблока, в течение spare_time образовался
        блок, который так и не исчез """
        self.photo_tracer_test_mask('EXTERNAL_PHOTOCELL', spare_time=4,
                                    block_after=3,
                                    normal_after=3, block_after_spare=2,
                                    thread_must_dead=False)


if __name__ == '__main__':
    unittest.main()
