""" Содержит объекты для тестов (экземпляры классов QSB, WeightSplitter и
прочее), которые импортируются тесты. Инициализация происходит в этом модуле
разово, так что нет необходимости их создавать в каждом тесте. """

from qodex_skud_bus.main import QodexSkudBus
from weightsplitter.main import WeightSplitter
from portdatasplitter.main import PortDataSplitter
from whikoperator.main import Wpicoperator
from wsqluse.wsqluse import Wsqluse


points_list = [
    {'point_name': 'EXTERNAL_GATE', 'point_num': 2,
     'point_type': 'EXTERNAL_GATE'},
    {'point_name': 'INTERNAL_GATE', 'point_num': 1,
     'point_type': 'INTERNAL_GATE'},
    {'point_name': 'INTERNAL_PHOTOCELL', 'point_num': 3,
     'point_type': 'INTERNAL_PHOTOCELL'},
    {'point_name': 'EXTERNAL_PHOTOCELL', 'point_num': 4,
     'point_type': 'EXTERNAL_PHOTOCELL'},
]
test_qsb = QodexSkudBus('192.168.100.109', 3312, points_list=points_list,
                        skud_test_mode=True)
weightsplitter_test = WeightSplitter('localhost', 1337, test_mode=True,
                                     debug=False,
                                     port_names_list=['TEST1'])
pds_test = PortDataSplitter('localhost', 1338,  test_mode=True)
cam_operator_test = Wpicoperator('192.168.100.139', 'admin', 'hect0r1337')
test_sql_shell = Wsqluse('wdb', 'watchman', 'hect0r1337', '192.168.100.118')

