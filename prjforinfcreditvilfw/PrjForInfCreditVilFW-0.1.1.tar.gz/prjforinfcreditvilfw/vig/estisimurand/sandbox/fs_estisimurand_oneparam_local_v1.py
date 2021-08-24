'''
Created on Nov 5, 2020

Simulation for estimation, to generate results for the first step for estimation over AWS.

@author: fan

Example Old Task Definition:
    - c-20180918-ITG-list-tall-mlt-ne1a2-1141--esti--ng-p-d-esti-thin-11-4-4--no-ge--multiprocess-c8m46080a1:1 (INACTIVE)
Link:
[['e', '20201025x_esti_tinytstthin_11_esr_beta', ['esti_param.beta'], None]]
    c_20180918_ITG_list_tall_mlt_ne1a2
    e_20201025x_esr_beta
    - https://s3.console.aws.amazon.com/s3/buckets/thaijmp201809j8vara?region=us-east-1&prefix=esti/c_20180918_ITG_list_tall_mlt_ne1a2/C4E79M4S4_c1036/json/&showversions=false
Sample Command:
    - Command ["python /ThaiJMP/invoke/run.py -A ng_s_d=esti_tstthin_11=4=4 -B c -C 20180815x_beta -D esti_param.beta -E 0 -F min_graphs -G esti --no-ge --no-multiprocess --esti"]

Estimate only with one simulation: (1) Randomly draw vectors of parameters within bounds.
(2) Estimate the model using each one of these vectors as initial parameter. (3) Do
not estimate fully, only let estimation proceed for one iteration. This means that we
are effectively using the estimation structure to simulate the model once at many parameter
values. Setting this in the context of estimation preserves the flexibility of potentially
letting estimation iterations to proceed for more than one round.

KEY PARAMETERS:

1. spekey: 'esti_spec_key': 'esti_thin_11' or 'esti_tstthin_11',
    see: parameters.runspecs.estimate_specs.estimate_set_gen
    need to set: esti_spec['esti_max_func_eval'] = 1
2. main_args: 'SAVE_DIRECTORY_MAIN': 'ESTI'
3. main_args: 'ESTIMATE': TRUE. This is important, because this will generate the overall moment
    objective based on all locations and times.
4. Decide if tt

at soluequi/param_loop.py:161, change Exception stopping criteria.
'''

import parameters.loop_combo_type_list.param_combo_type_list as paramcombotypelist
import parameters.runspecs.get_compesti_specs as param_compestispecs
import projectsupport.systemsupport as proj_sys_sup
import pyfan.devel.flog.logsupport as pyfan_logsup
import parameters.runspecs.estimate_specs as estispec
import invoke.run_main as invoke_run_main
import estimation.postprocess.process_main as esticomp
import os as os
import projectsupport.hardcode.string_shared as hardstring
from copy import deepcopy
import logging

# Initiate Log
spn_log = pyfan_logsup.log_vig_start(spt_root=proj_sys_sup.main_directory(),
                                     main_folder_name='logvig', sub_folder_name='estisimurand',
                                     subsub_folder_name='simu',
                                     file_name='fs_estisimurand_oneparam_local',
                                     it_time_format=8, log_level=logging.INFO)

# A. Specify Estimation Parameters and What do they mean


AR_STEPS = [1, 2]


# A. Common Arguments
# importantly, ESTI_TEST_11, DOES NOT HAVE SIMU at the end.
# This means moments will be generated, nad parameter values of beta will be randomly
# drawn rather than over meshed grid
graph_panda_list_name = 'min_graphs'
dc_speckey_default = {'compute_spec_key': 'ng_s_t',
                      'esti_spec_key': 'esti_tinytstthin_11',
                      'moment_key': 3,
                      'momset_key': 3}

# region_time_suffix = hardstring.region_time_suffix(moment_key=dc_speckey_default['moment_key'])

# B. Solve over grid of beta
for it_run in [1, 3]:

    dc_speckey_default_use = deepcopy(dc_speckey_default)
    bl_ge = False
    paramstr_key_list_str = ['list_tKap_mlt_ce1a2']

    if 'ce1a2' in paramstr_key_list_str:
        dc_speckey_default['moment_key'] = 3
    elif 'ne1a2' in paramstr_key_list_str:
        dc_speckey_default['moment_key'] = 4
    elif 'all_ne1a1ce1a1' in paramstr_key_list_str:
        dc_speckey_default['moment_key'] = 2

    combo_type_list_ab = 'e'
    if it_run == 1:
        # NON-INTEGRATED, NON-GE
        # Results stored in:
        #   C:\Users\fan\Documents\Dropbox (UH-ECON)\Project Dissertation\simu\e_20201025x_beta
        combo_type_list_date = '20201025x_esr'

    if it_run == 3:
        # INTEGRATED, NON-GE
        # Results stored in:
        #   C:\Users\fan\Documents\Dropbox (UH-ECON)\Project Dissertation\esti\e_20201025x_ITG_esti_tinytstthin_11_esr_beta
        combo_type_list_date = '20201025x_ITG_esr'

    # Generate combo_type
    combo_type_one = 'e'
    # [['e', '20201025x_esr_mlt_all_beta', ['esti_param.beta'], None]]
    ls_combo_type = paramcombotypelist.gen_combo_type_list(file=combo_type_list_ab, date=combo_type_list_date,
                                                           paramstr_key_list_str=paramstr_key_list_str)
    # run
    combo_type = ls_combo_type[0]
    # invoke/run_estimate.py:81c, subfolder name generation style
    srt_file_name = combo_type[0] + '_' + combo_type[1]

    """
    Step 1, Thin Estimate Many Points
    """

    # generate args
    dc_invoke_main_args = {'speckey': param_compestispecs.get_speckey_string(**dc_speckey_default_use),
                           'ge': bl_ge,
                           'multiprocess': False,
                           'estimate': True,
                           'graph_panda_list_name': 'min_graphs',
                           'save_directory_main': 'esti',
                           'logging_level': logging.WARNING,
                           'log_file': False,
                           'log_file_suffix': ''}


    # Number of points to randomly draw and estimate with one iteration at
    dc_estispec = estispec.estimate_set(dc_speckey_default['esti_spec_key'],
                                        moment_key=dc_speckey_default['moment_key'],
                                        momset_key=dc_speckey_default['momset_key'])
    esti_param_vec_count = dc_estispec['esti_param_vec_count']

    # estimate at each initial random points
    if 1 in AR_STEPS:
        for it_esti_ctr in range(esti_param_vec_count):
            # Update the 3rd element of combo_type, which determines which draw index to use
            combo_type[3] = it_esti_ctr
            try:
                invoke_run_main.invoke_main(combo_type, **dc_invoke_main_args)
            except Exception:
                logging.critical(f'Finished this {it_esti_ctr=} of {range(esti_param_vec_count)=}')

    """
    Step 2, Gather individual folder CSVs together, aggregate Excel with all simulations
    """

    # estimate at each initial random points
    paramstr_key_list = paramstr_key_list_str
    esti_spec_key = dc_speckey_default_use['esti_spec_key']
    search_directory = os.path.join(proj_sys_sup.main_directory(), 'esti', srt_file_name, '')

    if it_run == 1:
        exo_or_endo_graph_row_select = '_exo_wgtJ'

    if it_run == 3:
        exo_or_endo_graph_row_select = '_exoitg_wgtJitg'

    if 2 in AR_STEPS:
        esticomp.search_combine_indi_esti(paramstr_key_list,
                                          combo_type_list_ab,
                                          combo_type_list_date, esti_spec_key,
                                          moment_key=dc_speckey_default['moment_key'],
                                          momset_key=dc_speckey_default['momset_key'],
                                          exo_or_endo_graph_row_select=exo_or_endo_graph_row_select,
                                          image_save_name_prefix='AGG_ALLESTI_',
                                          search_directory=search_directory,
                                          fils_search_str=None,
                                          save_file_name=None,
                                          save_panda_all=True,
                                          graph_list=None,
                                          top_estimates_keep_count=2)
