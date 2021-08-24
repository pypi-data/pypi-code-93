'''
Created on Jun 7, 2018

@author: fan
'''

import time
import unittest
import logging

import parameters.loop_param_combo_list.loops_gen as paramloop
import projectsupport.systemsupport as proj_sys_sup
import numpy as np
import json

logger = logging.getLogger(__name__)

save_directory = proj_sys_sup.get_paths('model_test', sub_folder_name='test_param_loop')
FORMAT = '%(filename)s - %(funcName)s - %(lineno)d -  %(asctime)s - %(levelname)s %(message)s'
np.set_printoptions(precision=2, linewidth=100, suppress=True, threshold=3000)
logging.basicConfig(
    filename=save_directory + '/log_test_param_loops.py',
    filemode='w',
    level=logging.DEBUG, format=FORMAT)

class TestCombo(unittest.TestCase):

    def setUp(self):
        logger.debug('setup module')
        self.startTime = time.time()

    def tearDown(self):
        t = time.time() - self.startTime        
        logger.warning('%s: %s',self.id(), t)
        logger.debug('teardown module')

    def test_default(self):
        self.process_tests(param_type='esti_type', param_name='alpha_k')
        self.process_tests(param_type='esti_type', param_name='rho')
        
    def test2(self):
        self.process_tests(param_type='data_type', param_name='A')

    def test3(self):
        self.process_tests(param_type='grid_type', param_name='len_choices')
        
    def process_tests(self, test_log_name_prefix='',  
                      param_type='esti_type', param_name='alpha_k',
                      grid_f='a', grid_t='20180607',
                      esti_f='a', esti_t='20180607',
                      data_f='a', data_t='20180607',
                      model_f='a', model_t='a',
                      interpolant_f='a', interpolant_t='20180607'):
        
        combo_type = ['a', '20170702x_alphk', [param_type + '.' +param_name]]
        get_combo_list = paramloop.combo_list_auto(
                                combo_type=combo_type,
                                grid_f=grid_f, grid_t=grid_t,
                                esti_f=esti_f, esti_t=esti_t,
                                data_f=data_f, data_t=data_t,
                                model_f=model_f, model_t=model_t,
                                interpolant_f=interpolant_f, interpolant_t=interpolant_t)
        
        proj_sys_sup.jdump(get_combo_list, 'get_combo_list', logger=logger.info)
            


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
