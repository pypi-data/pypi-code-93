'''
Created on Aug 5, 2018

@author: fan

Testing Estimation Results Locally
'''

import unittest

import logging

import time
import invoke.local_estimate as estilocal
import projectsupport.systemsupport as proj_sys_sup

import numpy as np

logger = logging.getLogger(__name__)

'''
run_local has date timesufx, because the point is to care old and new
see if under coding changes, we are still producing the same results as before. 
And to monitor overall, how code changes are affecting results. 
'''
timesufx = '_' + proj_sys_sup.save_suffix_time(1)
saveDirectory = proj_sys_sup.get_paths('model_test', sub_folder_name='test_esti' + timesufx)


class TestRunLocal(unittest.TestCase):

    def setUp(self):
        logger.debug('setup module')
        self.startTime = time.time()

    def tearDown(self):
        t = time.time() - self.startTime
        logger.warning('%s: %s', self.id(), t)
        logger.debug('teardown module')

    def specs(self,
              esti_spec_key='nonespec',
              paramstr_key_list=['alpha_k'],
              moment_key=0, momset_key=1,
              run_size='x', integrated=False, equilibrium=False,
              graph_panda_list_name='main_graphs',
              fargate=False, ec2_start=False, run_docker=False,
              aws_type='fargate', job_queue=None):

        combo_type_list_ab = 'c'

        if (integrated):
            ITG = '_ITG'
        else:
            ITG = ''

        combo_type_list_date = '20180801' + run_size + ITG

        if (equilibrium):
            # 1:'ge-s-t-bis'
            invoke_set = 8
        else:
            # 1:'ng_s_t'
            invoke_set = 1

        save_directory_main = saveDirectory

        # log_file=False because doing logging here in line 88
        estilocal.estimate_local(invoke_set,
                                 esti_spec_key=esti_spec_key,
                                 combo_type_list_ab=combo_type_list_ab,
                                 combo_type_list_date=combo_type_list_date,
                                 paramstr_key_list=paramstr_key_list,
                                 moment_key=moment_key, momset_key=momset_key,
                                 graph_panda_list_name=graph_panda_list_name,
                                 save_directory_main=save_directory_main,
                                 aws_type=aws_type, job_queue=job_queue,
                                 fargate=fargate, ec2_start=ec2_start, run_docker=run_docker)

    #     def test_invoke_local_equilibrium(self, run_size='x'):
    #         self.esti_types_res(run_size=run_size, integrated=False, equilibrium=True)
    #     def test_invoke_local_partial(self, run_size='x'):
    #         self.esti_types_res(run_size=run_size, integrated=False, equilibrium=False)
    #
    #     def test_invoke_local_partial_integrated(self, run_size='x'):
    #         self.esti_types_res(run_size=run_size, integrated=True, equilibrium=False)
    #     def test_invoke_local_equilibrium_integrated(self, run_size='x'):
    #         self.esti_types_res(run_size=run_size, integrated=True, equilibrium=True)

    def test_invoke_local_joint_group(self, run_size='x', moment_key=0, momset_key=1):
        #         for run in [1,2,3,4,5]:
        for run in [4]:
            if (run == 1):
                graph_panda_list_name = 'min_graphs_esti'
                paramstr_key_list = ['list_policy_Fxc', 'logit_sd_scale', ['alpha_k', 'K_DEPRECIATION']]
            if (run == 2):
                graph_panda_list_name = 'min_graphs_esti'
                paramstr_key_list = 'list_policy_Fxc'
            if (run == 3):
                graph_panda_list_name = 'min_graphs_esti'
                paramstr_key_list = ['list_technology', 'list_preference', 'list_preference', 'list_all_params']
            if (run == 4):
                graph_panda_list_name = 'min_graphs_esti'
                paramstr_key_list = [['alpha_k', 'rho']]
            if (run == 5):
                graph_panda_list_name = 'min_graphs_esti'
                paramstr_key_list = ['beta']

            self.esti_types_res(paramstr_key_list=paramstr_key_list,
                                moment_key=moment_key, momset_key=momset_key,
                                graph_panda_list_name=graph_panda_list_name,
                                run_size='x')

    #             self.specs(paramstr_key_list = paramstr_key_list,
    #                        run_size=run_size,
    #                        integrated=False, equilibrium=False, graph_panda_list_name=graph_panda_list_name)

    def esti_types_res(self, paramstr_key_list=None,
                       moment_key=0, momset_key=1,
                       graph_panda_list_name='min_graphs_esti',
                       integrated=False, equilibrium=False,
                       run_size='x'):

        if (paramstr_key_list is None):
            paramstr_key_list = ['alpha_k']

        #         paramstr_key_list = [['alpha_k','rho']]
        #         for run in [11,12,13,21,22,23,31,32,33]:
        for run in [11, 21, 31]:
            # set to esti_main_: why not esti_test?, because esti_test stops after 10, before natural stop
            # that breaks code, can not finish rest of run and other starting points.
            esti_spec_key = 'esti_main_' + str(run)
            #             esti_spec_key = 'nonespec'
            self.specs(esti_spec_key=esti_spec_key,
                       paramstr_key_list=paramstr_key_list,
                       moment_key=moment_key, momset_key=momset_key,
                       run_size=run_size,
                       integrated=integrated, equilibrium=equilibrium,
                       graph_panda_list_name=graph_panda_list_name)


if __name__ == "__main__":
    '''
    Seems that this logger needs to be at the lowest level
    '''
    #     central_log = True
    #     if (central_log):
    #         np.set_printoptions(precision=2, linewidth=100, suppress=True, threshold=1000)
    #         FORMAT = '%(name)s - %(filename)s - %(funcName)s - %(lineno)d -  %(asctime)s - %(levelname)s %(message)s'
    #         np.set_printoptions(precision=2, linewidth=100, suppress=True, threshold=1000)
    #         logging.basicConfig(filename= saveDirectory + '/test_estilocal'+timesufx+'.py',
    #                             filemode='w',
    #                             level=logging.INFO, format=FORMAT)

    '''
    Start Unit Tests
    '''
    unittest.main()
