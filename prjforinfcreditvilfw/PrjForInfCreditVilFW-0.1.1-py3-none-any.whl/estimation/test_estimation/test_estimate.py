'''
Created on Apr 10, 2018

@author: fan
'''

import unittest

import logging
logger = logging.getLogger(__name__)

import estimation.estimate as estimate
import parameters.combo as paramcombo

import time
import numpy as np
import projectsupport.systemsupport as proj_sys_sup
saveDirectory = proj_sys_sup.get_paths('model_test', sub_folder_name='test_esti')
timesufx = proj_sys_sup.save_suffix_time()
timesufx = ''

class TestSolu(unittest.TestCase):

    def setUp(self):
        logger.debug('setup module')
        self.saveDirectory = saveDirectory           
        self.startTime = time.time()   
        self.timesufx = proj_sys_sup.save_suffix_time()
        
    def tearDown(self):
        t = time.time() - self.startTime
        logger.warning('%s: %s',self.id(), t)
        logger.debug('teardown module')

    def test_main(self):
        esti_method = 'MomentsSimuStates'
        params_esti_set = 0
        esti_option_type = 2
        moment_set = 0
        esti_func_type = 'nldmd'
        
        combo_type=['a', '20180403a']
        get_combo_list = paramcombo.get_combo(combo_type)

        estimate.estimate(esti_method, params_esti_set,
                          moment_set, esti_option_type,
                          esti_func_type, get_combo_list[0])
        
        

if __name__ == "__main__":
    
    FORMAT = '%(filename)s - %(funcName)s - %(lineno)d -  %(asctime)s - %(levelname)s %(message)s'
    np.set_printoptions(precision=5, linewidth=100, suppress=True, threshold=1000)
    logging.basicConfig(filename= saveDirectory + '/logesti'+timesufx+'.py',
                        filemode='w',
                        level=logging.DEBUG, format=FORMAT)
    unittest.main()

