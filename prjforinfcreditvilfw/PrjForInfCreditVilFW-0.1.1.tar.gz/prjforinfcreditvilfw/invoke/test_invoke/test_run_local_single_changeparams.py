'''
Created on Oct 21, 2020

@author: fan

Single set of parameter value.

Fully and freely specify core parameters to solve the model and generate all needed results.

1. PE run
2. PE + integrated run
3. GE + integrated run

There are additional parameters that need to be specified for (2) and (3).

(1), (2) and (3) all share certain parameters.

'''

import unittest
import logging

import time
import invoke.local_simulate as runlocal
import projectsupport.systemsupport as proj_sys_sup
import parameters.combo as param_combos
import pyfan.amto.json.json as support_json

import numpy as np

logger = logging.getLogger(__name__)

timesufx = '_' + proj_sys_sup.save_suffix_time(1)
srt_test_folder = 'test_runlocal_single_cp' + timesufx
saveDirectory = proj_sys_sup.get_paths('model_test', sub_folder_name=srt_test_folder)

FORMAT = '%(filename)s - %(funcName)s - %(lineno)d -  %(asctime)s - %(levelname)s %(message)s'
# np.set_printoptions(precision=4, linewidth=100, suppress=True, threshold=np.nan)
np.set_printoptions(precision=2, linewidth=100, suppress=True, threshold=3000)
logging.basicConfig(filename=saveDirectory + '/' + srt_test_folder + '.py',
                    filemode='w',
                    level=logging.DEBUG, format=FORMAT)

#
# def gen_compesti_spec()
#
#     esti_specs = {'esti_method': 'MomentsSimuStates',
#                   'moments_type': ['a', '20180805a'],
#                   'momsets_type': ['a', '20180805a'],
#                   'esti_option_type': 1,
#                   'esti_func_type': 'L-BFGS-B',
#                   'param_grid_or_rand': 'rand',
#                   'esti_param_vec_count': 1,
#                   'esti_max_func_eval': 10,
#                   'graph_frequncy': 20}
#
#     compute_specs = {'cpu': str(1024 * 1),
#                      'memory': str(517),  # only need about 160 mb in reality
#                      'workers': 1,
#                      'compute_param_vec_count': 14,
#                      'aws_fargate': False,
#                      'ge': False,
#                      'multiprocess': False,
#                      'graph': True}
#
#     compesti_specs = {**compute_specs, **esti_specs}
#
#     return compesti_specs


# def gen_combo_list()


# compesti_specs.update(cur_esti_spec)


if __name__ == "__main__":
    # unittest.main()
    compesti_specs_updates = {'esti_method': 'MomentsSimuStateszzz',
                              'moments_type': ['a', '20180805azzz'],
                              'momsets_type': ['a', '20180805azzz'],
                              'momsets_type_uuu': ['a', '20180805azzz']}

    compesti_specs = param_combos.gen_compesti_spec(it_default_group=None, **compesti_specs_updates)
    support_json.jdump(compesti_specs, 'compesti_specs', logger=logger.warning)
