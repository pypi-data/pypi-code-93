'''
Created on Jul 24, 2018

@author: fan

A vector of parameter values looping over testing

cd c:/Users/Fan/ThaiJMP/invoke/test_invoke
python test_run_local_simuvec.py
'''

import unittest

import logging

import time
import invoke.local_simulate as runlocal
import projectsupport.systemsupport as proj_sys_sup

import numpy as np

logger = logging.getLogger(__name__)
'''
run_local has date timesufx, because the point is to care old and new
see if under coding changes, we are still producing the same results as before.
And to monitor overall, how code changes are affecting results.
'''
timesufx = '_' + proj_sys_sup.save_suffix_time(1)
saveDirectory = proj_sys_sup.get_paths('model_test', sub_folder_name='test_runlocal_simuvec' + timesufx)

class TestRunLocal(unittest.TestCase):

    def setUp(self):
        logger.debug('setup module')
        self.startTime = time.time()

    def tearDown(self):
        t = time.time() - self.startTime
        logger.warning('%s: %s', self.id(), t)
        logger.debug('teardown module')

    def specs(self,
              paramstr_key_list=['beta'],
              moment_key=0, momset_key=1,
              run_size='x', integrated=False, equilibrium=False,
              graph_panda_list_name='all_graphs_tables',
              fargate=False, ec2_start=False, run_docker=False):

        combo_type_list_ab = 'e'

        if (integrated):
            ITG = '_ITG'
        else:
            ITG = ''

        # combo_type_list_date = '20180702' + run_size + ITG
        combo_type_list_date = '20200901' + run_size + ITG + '_7jAll'

        if (equilibrium):
            # 1:'ge-s-t-bis'--fargate_ge_bis_t_seq
            invoke_set = 8
        else:
            # 1:'ng_s_t'--fargate_ng_seq_t
            invoke_set = 1

        save_directory_main = saveDirectory

        # log_file=False because doing logging here in line 88
        runlocal.run_here(invoke_set,
                          combo_type_list_ab=combo_type_list_ab,
                          combo_type_list_date=combo_type_list_date,
                          paramstr_key_list=paramstr_key_list,
                          moment_key=moment_key, momset_key=momset_key,
                          save_directory_main=save_directory_main,
                          graph_panda_list_name=graph_panda_list_name,
                          fargate=fargate,
                          ec2_start=ec2_start, run_docker=run_docker,
                          logging_level=logging.INFO,
                          log_file=True)

    def test_invoke_local_partial(self, run_size='x'):
        graph_panda_list_name = 'all_graphs_tables'
        self.specs(run_size=run_size, integrated=False, equilibrium=False, graph_panda_list_name=graph_panda_list_name)

    def test_invoke_local_partial_integrated(self, run_size='x'):
        self.specs(run_size=run_size, integrated=True, equilibrium=False)

    def test_invoke_local_equilibrium(self, run_size='x'):
        self.specs(run_size=run_size, integrated=False, equilibrium=True)

    def test_invoke_local_equilibrium_integrated(self, run_size='x'):
        self.specs(run_size=run_size, integrated=True, equilibrium=True)

    def test_invoke_local_joint_group_call(self):
        self.test_invoke_local_joint_group(run_size='x', integrated=False)

    def test_invoke_local_joint_group(self, run_size='x', integrated=True):
        for run in [1, 2, 3, 4, 5]:
            if (run == 1):
                graph_panda_list_name = 'min_graphs'
                paramstr_key_list = ['list_policy_Fxc', ['alpha_k', 'beta'], 'alpha_k']
            if (run == 2):
                graph_panda_list_name = 'min_graphs'
                paramstr_key_list = 'list_policy_Fxc'
            if (run == 3):
                graph_panda_list_name = 'all_graphs_tables'
                paramstr_key_list = ['logit_sd_scale']
            if (run == 4):
                graph_panda_list_name = 'min_graphs'
                paramstr_key_list = ['beta']
            if (run == 5):
                graph_panda_list_name = 'min_graphs'
                paramstr_key_list = [['rho', 'BNF_SAVE_P']]

            self.specs(paramstr_key_list=paramstr_key_list,
                       run_size=run_size,
                       integrated=integrated, equilibrium=False,
                       graph_panda_list_name=graph_panda_list_name)


if __name__ == "__main__":

    '''
    Seems that this logger needs to be at the lowest level
    '''
    central_log = True

    if central_log:
        pass

        # np.set_printoptions(precision=2, linewidth=100, suppress=True, threshold=1000)

        #   Can not see to set different logging levels when getting logger all from root logger
        #   Seems like if I want to actually have different log files outputting at different levels, need different loggers specified.
        #   Although that seems to be different from what the documentation states.

        # FORMAT = '%(name)s - %(filename)s - %(funcName)s - %(lineno)d -  %(asctime)s - %(levelname)s %(message)s'
        # np.set_printoptions(precision=2, linewidth=100, suppress=True, threshold=1000)
        # logging.basicConfig(filename=saveDirectory + '/test_runlocalsingle' + timesufx + '.py',
        #                     filemode='w',
        #                     level=logging.INFO, format=FORMAT)

    #     CAN NOT OVERRIDE DEFAULT WARNING IT SEEMS WITH CODES BELOW
    #     FORMAT = '%(filename)s - %(funcName)s - %(lineno)d -  %(asctime)s - %(levelname)s %(message)s'
    #     debug_fh = logging.FileHandler(saveDirectory + '/test_runlocalsimuvec'+timesufx+'_warning.log',
    #                                    mode='w')
    #     debug_fh.setLevel(logging.WARNING)
    #     debug_fh.setFormatter(logging.Formatter(FORMAT))
    #     logging.getLogger('').addHandler(debug_fh)

    #     '''
    #     Handler for Debug level: fh for file_handler
    #     '''
    #     DEBUG_FORMAT = '%(name)s - %(filename)s - %(funcName)s - %(lineno)d -  %(asctime)s - %(levelname)s %(message)s'
    #     info_fh = logging.FileHandler(saveDirectory + '/test_runlocalsimuvec'+timesufx+'_info.log')
    #     info_fh.setLevel(logging.INFO)
    #     info_fh.setFormatter(logging.Formatter(DEBUG_FORMAT))
    #     # add to root logger
    #     logging.getLogger('').addHandler(info_fh)

    #     '''
    #     Handler for Console
    #     '''
    #     CONSOLE_FORMAT = '%(name)-12s: %(levelname)-8s %(message)s'
    #     console = logging.StreamHandler()
    #     console.setLevel(logging.WARNING)
    #     # tell the handler to use this format
    #     console.setFormatter(logging.Formatter(CONSOLE_FORMAT))
    #     # add the handler to the root logger
    #     logging.getLogger('').addHandler(console)

    '''
    Start Unit Tests
    '''
    unittest.main()
