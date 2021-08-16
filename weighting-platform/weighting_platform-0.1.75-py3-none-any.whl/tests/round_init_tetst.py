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
            {'point_name': 'EXTERNAL_GATE', 'point_num': 2, 'point_type': 'EXTERNAL_GATE'},
            {'point_name': 'INTERNAL_GATE', 'point_num': 1, 'point_type': 'EXTERNAL_GATE'},
            {'point_name': 'INTERNAL_PHOTOCELL', 'point_num': 4, 'point_type': 'INTERNAL_PHOTOCELL'},
            {'point_name': 'EXTERNAL_PHOTOCELL', 'point_num': 3, 'point_type': 'EXTERNAL_PHOTOCELL'}
            ]
        self.db_worker = Recorder('wdb', 'watchman', 'hect0r1337',
                                  '192.168.100.118')
        self.qsb = QodexSkudBus('192.168.100.109', 3312, self.points_list,
                                skud_test_mode=False)
        self.qco = Wpicoperator('192.168.100.139', 'admin', 'hect0r1337')
        self.weight_splitter = WeightSplitter('localhost', 2292,
                                              test_mode=True)
        self.weight_platform = WeightingPlatform(self.qsb, self.qco,
                                                 self.db_worker,
                                                 self.weight_splitter)

    def test_init_record_block_first(self):
        """ Тестирование заезда с блоком первого фотоэлемента и без ее деблока """
        self.weight_platform.init_round('В060ХА702',
                                         'external',
                                         'auto',
                                         0,
                                         0,
                                         1,
                                         1,
                                         1,
                                         'INIT_TEST',
                                         16)

if __name__ == '__main__':
    unittest.main()
