'''
Created on Mar 27, 2018

@author: fan
'''
import unittest

import logging

import numpy as np

import time
import solusteady.simuinterp as simu
import pyfan.util.inout.exportpanda as exportpanda
import projectsupport.systemsupport as proj_sys_sup

logger = logging.getLogger(__name__)

saveDirectory = proj_sys_sup.get_paths('model_test', sub_folder_name='test_simuinterp')

FORMAT = '%(filename)s - %(funcName)s - %(lineno)d -  %(asctime)s - %(levelname)s %(message)s'
np.set_printoptions(precision=4, linewidth=100, suppress=True, threshold=np.nan)
np.set_printoptions(precision=2, linewidth=100, suppress=True, threshold=3000)
logging.basicConfig(filename=saveDirectory + '/logsimuinterp.py',
                    filemode='w',
                    level=logging.DEBUG, format=FORMAT)


class TestSimuAnalytical(unittest.TestCase):

    def setUp(self):
        logger.debug('setup module')
        self.startTime = time.time()

    def tearDown(self):
        t = time.time() - self.startTime
        logger.warning('%s: %s', self.id(), t)
        logger.debug('teardown module')

    def testMain(self):
        grid_type = ['a', 42]
        esti_type = ['a', 1]
        data_type = ['a']
        param_update_dict = {'grid_type': grid_type,
                             'esti_type': esti_type,
                             'data_type': data_type}
        store, store_map = simu.simu_interp(param_update_dict)
        file_prefix = 'simu_' + \
                      grid_type[0] + '_' + str(grid_type[1]) + '_' + \
                      esti_type[0] + '_' + str(esti_type[1])

        hist_len = int(store.size / len(store_map))
        var_len = len(store_map)

        store = np.reshape(store, (hist_len, var_len))
        exportpanda.export_history_csv(store, store_map, saveDirectory, file_prefix)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
