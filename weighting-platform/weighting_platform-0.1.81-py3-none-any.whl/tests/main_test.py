import datetime
import unittest
from weighting_platform.main import WeightingPlatform
from gravityRecorder.main import Recorder
from qodex_skud_bus.main import QodexSkudBus
from whikoperator.main import Wpicoperator
from weightsplitter.main import WeightSplitter
import time
import threading


class MainTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(MainTest, self).__init__(*args, **kwargs)
        self.points_list = [
            {'point_name': 'EXTERNAL_BARRIER', 'point_num': 2, 'point_type': 'EXTERNAL_GATE'},
            {'point_name': 'INTERNAL_BARRIER', 'point_num': 1, 'point_type': 'INTERNAL_GATE'},
            {'point_name': 'INTERNAL_PHOTOCELL', 'point_num': 3, 'point_type': 'INTERNAL_PHOTOCELL'},
            {'point_name': 'EXTERNAL_PHOTOCELL', 'point_num': 4, 'point_type': 'EXTERNAL_PHOTOCELL'}
            ]
        self.db_worker = Recorder('wdb', 'watchman', 'hect0r1337',
                                  '192.168.100.118')
        self.qsb = QodexSkudBus('192.168.100.109', 3312, self.points_list,
                                skud_test_mode=True)
        self.qco = Wpicoperator('192.168.100.139', 'admin', 'hect0r1337')
        self.weight_splitter = WeightSplitter('localhost', 2292,
                                              test_mode=True)
        self.weight_platform = WeightingPlatform(self.qsb, self.qco,
                                                 self.db_worker,
                                                 self.weight_splitter)


    #@unittest.skip('Reason for skipping')
    def test_init_record_normal(self):
        """ Тестирование обычного заезда """
        main_thread = threading.Thread(target=self.weight_platform.init_round,
                                             args=('В060ХА702',
                                                   'external',
                                                   'auto',
                                                   0,
                                                   0,
                                                   1,
                                                   1,
                                                   1,
                                                   'INIT_TEST',
                                                   16))
        main_thread.start()
        time.sleep(3)
        print("LOCKING EXTERNAL", datetime.datetime.now())
        self.qsb.lock_point('EXTERNAL_PHOTOCELL')
        time.sleep(3)
        self.weight_splitter.set_manual_value(manual_value=300)
        self.weight_splitter.set_manual_value(manual_value=1000)
        self.qsb.normal_point('EXTERNAL_PHOTOCELL')
        self.weight_splitter.set_manual_value(manual_value=5000)
        time.sleep(1)
        print('CHANGING! TO 1000')
        self.weight_splitter.set_manual_value(manual_value=10000)
        time.sleep(3)
        print('CHANGING! TO 15000')
        self.weight_splitter.set_manual_value(manual_value=15000)
        time.sleep(16)
        print('CHANGING! TO 0')
        self.weight_splitter.set_manual_value(manual_value=10)
        print("LOCKING INTERNAL", datetime.datetime.now())
        self.qsb.lock_point('INTERNAL_PHOTOCELL')
        time.sleep(2)
        print('NORMAL_PHOTOCELL')
        self.qsb.normal_point('INTERNAL_PHOTOCELL')
        time.sleep(8)
        self.assertTrue(not main_thread.is_alive())

    #@unittest.skip('Reason for skipping')
    def test_init_record_block_first(self):
        """ Тестирование заезда с блоком первого фотоэлемента и без ее деблока """
        main_thread = threading.Thread(target=self.weight_platform.init_round,
                                       args=('В060ХА702',
                                             'external',
                                             'auto',
                                             0,
                                             0,
                                             1,
                                             1,
                                             1,
                                             'INIT_TEST',
                                             16))
        main_thread.start()
        time.sleep(3)
        print("LOCKING EXTERNAL", datetime.datetime.now())
        self.qsb.lock_point('EXTERNAL_PHOTOCELL')
        time.sleep(15)
        self.assertTrue(main_thread.is_alive())

    #@unittest.skip('Reason for skipping')
    def test_init_record_without_exit(self):
        """ Тестирование заезда с отсутствием съезда с весов """
        main_thread = threading.Thread(target=self.weight_platform.init_round,
                                       args=('В060ХА702',
                                             'external',
                                             'auto',
                                             0,
                                             0,
                                             1,
                                             1,
                                             1,
                                             'INIT_TEST',
                                             16))
        main_thread.start()
        time.sleep(3)
        print("LOCKING EXTERNAL", datetime.datetime.now())
        self.qsb.lock_point('EXTERNAL_PHOTOCELL')
        time.sleep(3)
        self.weight_splitter.set_manual_value(manual_value=300)
        self.weight_splitter.set_manual_value(manual_value=1000)
        self.qsb.normal_point('EXTERNAL_PHOTOCELL')
        self.weight_splitter.set_manual_value(manual_value=5000)
        time.sleep(1)
        print('CHANGING! TO 1000')
        self.weight_splitter.set_manual_value(manual_value=10000)
        time.sleep(3)
        print('CHANGING! TO 15000')
        self.weight_splitter.set_manual_value(manual_value=15000)
        time.sleep(10)
        print("LOCKING INTERNAL", datetime.datetime.now())
        self.qsb.lock_point('INTERNAL_PHOTOCELL')
        self.qsb.normal_point('INTERNAL_PHOTOCELL')
        time.sleep(10)
        self.assertTrue(main_thread.is_alive())

    def test_init_record_dlinnomer(self):
        """ Тестирование заезда с протоколом длинномер """
        main_thread = threading.Thread(target=self.weight_platform.init_round,
                                       args=('В060ХА702',
                                             'external',
                                             'auto',
                                             1,
                                             0,
                                             1,
                                             1,
                                             1,
                                             'INIT_TEST',
                                             16))
        main_thread.start()
        time.sleep(10)
        self.qsb.lock_point('EXTERNAL_PHOTOCELL')
        time.sleep(9)
        self.weight_splitter.set_manual_value(manual_value=300)
        self.weight_splitter.set_manual_value(manual_value=1000)
        self.qsb.normal_point('EXTERNAL_PHOTOCELL')
        self.weight_splitter.set_manual_value(manual_value=5000)
        time.sleep(1)
        self.weight_splitter.set_manual_value(manual_value=10000)
        time.sleep(4)
        self.weight_splitter.set_manual_value(manual_value=15000)
        time.sleep(10)
        ex_gate_state = self.qsb.get_point_state('EXTERNAL_BARRIER')
        self.assertTrue(ex_gate_state == self.qsb.get_unlock_state_str())
        ex_gate_state = self.qsb.get_point_state('INTERNAL_BARRIER')
        self.assertTrue(ex_gate_state == self.qsb.get_unlock_state_str())
        time.sleep(3)
        self.weight_splitter.set_manual_value(manual_value=10000)
        self.qsb.lock_point('INTERNAL_PHOTOCELL')
        time.sleep(15)
        ex_gate_state = self.qsb.get_point_state('EXTERNAL_BARRIER')
        self.assertTrue(ex_gate_state == self.qsb.get_lock_state_str())
        ex_gate_state = self.qsb.get_point_state('INTERNAL_BARRIER')
        self.assertTrue(ex_gate_state == self.qsb.get_unlock_state_str())
        self.qsb.normal_point('INTERNAL_PHOTOCELL')
        time.sleep(10)
        self.weight_splitter.set_manual_value(manual_value= 10)
        self.qsb.normal_point('INTERNAL_PHOTOCELL')
        time.sleep(6)
        print('\n\n\n\nЗавершение тестов')
        self.assertTrue(not main_thread.is_alive())

if __name__ == '__main__':
    unittest.main()