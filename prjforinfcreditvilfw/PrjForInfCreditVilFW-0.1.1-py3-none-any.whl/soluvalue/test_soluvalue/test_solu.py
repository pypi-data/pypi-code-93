'''
Created on Feb 15, 2018

@author: fan
'''
import unittest

import logging

import time
import soluvalue.solu as solu
import numpy as np

import parameters.combo as paramcombo
# import projectsupport.graph.optimal_cates7 as opti7graph
# import projectsupport.graph.optimal_continuous as opticts
# import projectsupport.graph.optimal_maxj_policyphase as graph_phase
import analyze.analyzesolu as analyzesolu
import projectsupport.systemsupport as proj_sys_sup
import projectsupport.graph.graph_sets as sup_graphset

save_directory = proj_sys_sup.get_paths('model_test', sub_folder_name='test_solu')
timesufx = '_' + proj_sys_sup.save_suffix_time()
timesufx = ''

logger = logging.getLogger(__name__)

FORMAT = '%(filename)s - %(funcName)s - %(lineno)d -  %(asctime)s - %(levelname)s %(message)s'
np.set_printoptions(precision=2, linewidth=100, suppress=True, threshold=1000)
logging.basicConfig(filename=save_directory + '/logsolu' + timesufx + '.py',
                    filemode='w',
                    level=logging.DEBUG, format=FORMAT)


class TestSolu(unittest.TestCase):

    def setUp(self):
        logger.debug('setup module')
        self.save_directory = save_directory
        self.startTime = time.time()

    def tearDown(self):
        t = time.time() - self.startTime
        logger.warning('%s: %s', self.id(), t)
        logger.debug('teardown module')

    def test_combos_one(self):
        combo_type = ['a', '20180403a']
        #         combo_type=['a', '20180417a']
        #         combo_type=['a', '20180418a']
        combo_type = ['a', '20180418b']
        combo_type = ['a', '20180419a']
        #         combo_type=['a', '20180501a']
        combo_type = ['a', '20180506a']
        combo_type = ['a', '20180508']

        #         self.solve_from_combo_type(combo_type)

        combo_type = ['b', '20180613_basic']

        combo_type_list = [['a', '20180512_bench_nofc_J2'],
                           ['b', '20180613_basicJ5'],
                           ['b', '20180701_basicJ7']]

        # combo_type_list = [['b', '20180701_basicJ7']]
        #
        combo_type_list = [['a', '20180512_bench_nofc_J2']]

        combo_type_list = [['e', '20180801']]

        for combo_type in combo_type_list:
            self.solve_from_combo_type(combo_type)

    def solve_from_combo_type(self, combo_type):

        get_combo_list = paramcombo.get_combo(combo_type)
        for param_combo in get_combo_list:
            self.solve_graph_main(param_combo=param_combo,
                                  title=param_combo['title'],
                                  file_save_suffix=param_combo['file_save_suffix'],
                                  combo_desc=param_combo['combo_desc'])

    def Atest_a3a1(self):
        grid_type = ['a', 3]
        esti_type = ['a', 3]
        interpolant_type = ['a', 11]
        param_update_dict = {'grid_type': grid_type, 'esti_type': esti_type,
                             'interpolant_type': interpolant_type}
        param_combo = {'param_update_dict': param_update_dict}
        self.solve_graph_main(param_combo=param_combo,
                              title='basic',
                              file_save_suffix='_basic',
                              combo_desc='basic')

    def solve_graph_main(self, param_combo=None,
                         title='basic',
                         file_save_suffix='_basic',
                         combo_desc='basic'):

        directory_str_dict = {'title': title,
                              'file_save_suffix': file_save_suffix + timesufx,
                              'combo_desc': combo_desc,
                              'log': save_directory,
                              'csv': save_directory,
                              'csv_detail': save_directory,
                              'img_detail': save_directory,
                              'img_detail_indi': save_directory}

        # all_graphs_tables: has zooming in detailed graphs
        graph_panda_list_name = 'all_graphs_tables'
        # no zooming in detailed graphs
        graph_panda_list_name = 'all_solu_graphs_tables'
        graph_list = sup_graphset.graph_panda_sets_names(graph_panda_list_name)

        interpolant, solu_dict, mjall_inst, param_inst = solu.solve_model(
            param_combo=param_combo,
            directory_str_dict=directory_str_dict,
            graph_list=graph_list)

        analyzesolu.solve_graph_main(solu_dict, mjall_inst, param_inst,
                                     directory_str_dict,
                                     graph_list=graph_list)


if __name__ == "__main__":
    unittest.main()
