'''
Created on Jul 25, 2018

@author: fan

Single set of parameter value. Test using unittest.
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

This is only for testing simulation at a single point, not along a vector of points.

But this single point could be solved involving the need to simulate over an array
of productivity shock levels. Or could be solved over as GE.
'''
timesufx = '_' + proj_sys_sup.save_suffix_time(1)
saveDirectory = proj_sys_sup.get_paths('model_test', sub_folder_name='test_runlocal_single' + timesufx)

FORMAT = '%(filename)s - %(funcName)s - %(lineno)d -  %(asctime)s - %(levelname)s %(message)s'
# np.set_printoptions(precision=4, linewidth=100, suppress=True, threshold=np.nan)
np.set_printoptions(precision=2, linewidth=100, suppress=True, threshold=3000)
logging.basicConfig(filename=saveDirectory + '/test_runlocalsingle' + timesufx + '.py',
                    filemode='w',
                    level=logging.DEBUG, format=FORMAT)



class TestRunLocal(unittest.TestCase):

    def setUp(self):
        logger.debug('setup module')
        self.startTime = time.time()

    def tearDown(self):
        t = time.time() - self.startTime
        logger.warning('%s: %s', self.id(), t)
        logger.debug('teardown module')

    def should_also_test_2_5_7_choices(self):
        pass

    def specs_single_runs(self, integrated=False, equilibrium=False,
                          graph_panda_list_name='main_graphs',
                          fargate=False, ec2_start=False, run_docker=False):
        """
        These debug runs below has single parameter, not  avector of parameters
        these do not have x verion, just full runs, import test, testing full.

        Testing Equilibrium and Integration separately than jointly.

        combo_type_list_ab = 'b'
        combo_type_list_date = 20180717debug_beta
        paramstr_key_list:
          - what parameters to loop over

        combo_type_list_ab, combo_type_list_date, and paramstr_key_list jointly construct combo type list
          - parameters/loop_combo_type_list/param_combo_type_list.py, generates combo_type list based on 'ab', 'date' and what parameter to loop over.

        """
        combo_type_list_ab = 'b'
        combo_type_list_date_list = ['20180717debug_fcib',
                                     '20180717debug_alpk',
                                     '20180717debug_beta',
                                     '20180717debug_depr',
                                     '20180717debug_kapp',
                                     '20180916debug_lgit']
        combo_type_list_date_list = ['20180917debug_lgitlowR']
        combo_type_list_date_list = ['20180717debug_beta']

        combo_type_list_ab = 'e'
        combo_type_list_date_list = ['20180801']
        combo_type_list_date_list = ['20201025']

        debug_level = logging.DEBUG

        paramstr_key_list = None
        for combo_type_list_date in combo_type_list_date_list:
            if (integrated):
                ITG = '_ITG'
            else:
                ITG = ''

            if (integrated is True) and (equilibrium is False):
                invoke_set = 4

            elif (equilibrium):
                # this will include both integraed and non-integrated runs
                # 1:'ge-s-t-bis'
                invoke_set = 8
            else:
                # 1:'ng_s_t'
                invoke_set = 1

            save_directory_main = saveDirectory
            combo_type_list_date = combo_type_list_date + ITG

            runlocal.run_here(invoke_set,
                              combo_type_list_ab=combo_type_list_ab,
                              combo_type_list_date=combo_type_list_date,
                              paramstr_key_list=paramstr_key_list,
                              save_directory_main=save_directory_main,
                              graph_panda_list_name=graph_panda_list_name,
                              fargate=fargate,
                              ec2_start=ec2_start, run_docker=run_docker,
                              logging_level=debug_level,
                              log_file=True)

    def test_single_runs(self):
        graph_panda_list_name = 'all_graphs_tables'
        graph_panda_list_name = 'main_graphs'
        graph_panda_list_name = 'main_aAcsv_graphs'
        self.specs_single_runs(integrated=False, equilibrium=False, graph_panda_list_name=graph_panda_list_name)

    def test_single_runs_itg(self):
        graph_panda_list_name = 'main_aAcsv_graphs'
        self.specs_single_runs(integrated=True, equilibrium=False, graph_panda_list_name=graph_panda_list_name)

    def test_single_runs_ge(self):
        graph_panda_list_name = 'all_graphs_tables'
        graph_panda_list_name = 'main_graphs'
        graph_panda_list_name = 'main_aAcsv_graphs'
        # self.specs_single_runs(integrated=True, equilibrium=False, graph_panda_list_name=graph_panda_list_name)
        # self.specs_single_runs(integrated=False, equilibrium=True, graph_panda_list_name=graph_panda_list_name)
        self.specs_single_runs(integrated=False, equilibrium=True, graph_panda_list_name=graph_panda_list_name)

    def test_single_runs_itg_ge(self):
        graph_panda_list_name = 'main_aAcsv_graphs'
        self.specs_single_runs(integrated=True, equilibrium=True, graph_panda_list_name=graph_panda_list_name)



if __name__ == "__main__":
    unittest.main()
