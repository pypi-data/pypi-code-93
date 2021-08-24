"""
Created on Nov 16, 2020

There are four groups of decisions:

    Simulation Decisions (SD):
    Regardless of the estimation structure, at each parameter combination, how should simulation be done.

    Estimation Decisions (ED):
    Estimation related Specifications and decisions

    Compute Decisions (ED):
    Computational structure specifications

    Output Decisions (ED):
    What results to spit how, what to show from estimation/simulation.

There is a Number of different types of parameters to choose pick determine:

1. range of parameter values and other parameter specifications for all the parameters.
2. over which parameters to estimate the model, which parameters are free Parameters
3. how the model should be simulated, GE or not, Integrated or not. Many other decisions related to how the model should be simulated, most related to parameters/model specifications.
4. region and time periods for estimation, allowing which parameters to vary, and to jointly try to match outcomes in several regions and/or time periods.
5. how many points at which to do ESR draws for simulation
6. computational structure, if local, or remote, whether parallel processing should be used, and if using remote the compute requirements
7. where to store results, and what graphs/tables etc to save and to output.

Functions to Rely on:

    ESTIMATION FUNCTION

    AGGREGATION FUNCTION

    each of the function needs to be called several times. To facilitate calling them, their parameters are organized
    in a dictionary, which is modified for particular invokcations.
"""

import logging
import unittest


import parameters.loop_combo_type_list.param_combo_type_list as paramcombotypelist
import parameters.runspecs.get_compesti_specs as param_compestispecs
import projectsupport.systemsupport as proj_sys_sup
import pyfan.devel.flog.logsupport as pyfan_logsup
import parameters.runspecs.estimate_specs as estispec
import invoke.run_main as invoke_run_main
import estimation.postprocess.process_main as esticomp
import os as os
import projectsupport.hardcode.string_shared as hardstring
import parameters.parse_combo_type as parsecombotype
from copy import deepcopy
import logging

logger = logging.getLogger(__name__)

# Initiate Log
spn_log = pyfan_logsup.log_vig_start(spt_root=proj_sys_sup.main_directory(),
                                     main_folder_name='logvig', sub_folder_name='estisimurand',
                                     subsub_folder_name='oneparam_local',
                                     file_name='fs_estisimurand_oneparam_lin',
                                     it_time_format=8, log_level=logging.INFO)

class TestCombo(unittest.TestCase):

    def setUp(self):
        logger.debug('setup module')

    def tearDown(self):
        logger.debug('teardown module')

    def test(self):

        it_execute_type = 2
        if it_execute_type == 1:
            # quick run test
            # D:\repos\ThaiJMP\esti
            st_xd = 'x'
            st_file_suffix = '_esr_tstN5_vig'
            st_testscale = 'tinytst'
        elif it_execute_type == 2:
            # takes much longer and is larger
            # D:\repos\ThaiJMP\esti
            st_xd = ''
            st_file_suffix = '_esr_tstN100_vig'
            st_testscale = 'medtst'
        else:
            pass

        # Specify to estimate
        estimate = True
        # ar_steps meaning
        """
        Eight Elements of Esti-Simu-Rand
        1. Simulate at N sets of parameter combinations
        2. Polynomial approximation surface based on (1) for each outcome of interest, find best
        3. Estimation at N sets of starting points with (2) as objective function
        4. Gather results frorm (3), find M best.
        5. Simulate (estimate once) at the top M best results from (4) actual model, compare objective to approximated from (3)
        6. Gather results from (5), re-rank best of the M best from (4)
        7. Estimate at the top M best results from (4) actual model, (4) M best are M best seeds
        8. Gather results from (7), re-rank best of the final results from the M best seeds
        """

        ar_steps = [1, 2, 3, 4, 5, 6, 7, 8]
        ar_steps = [7]
        # need to be central first then northeast, by design
        ar_regions = ['ce', 'ne']

        # 1. range of parameter values and other parameter specifications for all the parameters.
        combo_type_list_ab = 'e'
        combo_type_list_date_base = '20201025'

        # 2. over which parameters to estimate the model, which parameters are free Parameters
        # value need to be list, not string
        dc_paramstr_key_list_str = {'ce': ['list_tKap_mlt_ce1a2'], 'ne': ['list_tKap_mlt_ne1a2']}

        # 3. how the model should be simulated, GE or not, Integrated or not. Many other decisions related to how the
        # model should be simulated, most related to parameters/model specifications.
        bl_ge = False

        combo_type_list_date = combo_type_list_date_base + st_xd

        # combo_type_list_date = combo_type_list_date + '_ITG_esr'
        # exo_or_endo_graph_row_select = '_exoitg_wgtJitg'
        combo_type_list_date = combo_type_list_date + st_file_suffix
        exo_or_endo_graph_row_select = '_exo_wgtJ'

        # 4. region and time periods for estimation, allowing which parameters to vary, and to jointly try to match
        # outcomes in several regions and/or time periods.
        dc_moment_key = {'ce': 3, 'ne': 4}
        momset_key = 3

        # 5. how many points at which to do ESR draws for simulation
        # the two esti_specs below share the same ESTI_PARAM_VEC_COUNT

        # "_1" = nelder meand and very lax tolerance
        esti_spec_key_esr1 = 'esti_' + st_testscale + '_thin_1'
        esti_spec_key_esr3 = 'esti_' + st_testscale + '_mpoly_13'
        esti_spec_key_esr5 = 'esti_mplypostsimu_1'
        esti_spec_key_esr7 = 'esti_mplypostesti_2'

        # 6. computational structure, if local, or remote, whether parallel processing should be used, and if using
        # remote the compute requirements
        # When local invoke the options don't matter much? except for worker count?
        multiprocess = False
        compute_spec_key_esr1 = 'ng_s_t'
        compute_spec_key_esr3 = 'mpoly_1'
        compute_spec_key_esr5 = 'ng_s_t'
        compute_spec_key_esr7 = compute_spec_key_esr5

        # 7. where to store results, and what graphs/tables etc to save and to output.
        graph_panda_list_name_esr1 = 'min_graphs'
        graph_panda_list_name_esr3 = 'min_graphs'
        graph_panda_list_name_esr5 = 'min_graphs'
        graph_panda_list_name_esr7 = 'min_graphs'
        save_directory_main = 'esti'
        log_file = False

        # Top results to keep
        # Random simulate points, grab out top five (objective) for review
        top_estimates_keep_count_esr2 = 5
        # MPOLY estimation all random points, top 5 results
        top_estimates_keep_count_esr4 = 5
        top_estimates_keep_count_esr6 = 5
        # At which'th top result to do full estimation
        ls_it_esti_top_which = [1, 2, 3, 4, 5]
        # Present which full estimation with mpoly best seeds
        top_estimates_keep_count_esr8 = 5

        # A. Common Arguments
        # importantly, ESTI_TEST_11, DOES NOT HAVE SIMU at the end.
        # This means moments will be generated, nad parameter values of beta will be randomly
        # drawn rather than over meshed grid
        dc_combo_type_kwargs = {'file': combo_type_list_ab, 'date': combo_type_list_date,
                                'paramstr_key_list_str': dc_paramstr_key_list_str['ce']}
        combo_type_ce = paramcombotypelist.gen_combo_type_list(**dc_combo_type_kwargs)[0]
        dc_combo_type_kwargs['paramstr_key_list_str'] = dc_paramstr_key_list_str['ne']
        combo_type_ne = paramcombotypelist.gen_combo_type_list(**dc_combo_type_kwargs)[0]
        dc_combo_type = {'ce': combo_type_ce, 'ne': combo_type_ne}

        """
        Step 1, default kwargs for key functions
        """

        dc_speckey_default = {'compute_spec_key': None,
                              'esti_spec_key': None,
                              'moment_key': None,
                              'momset_key': momset_key}
        # MPOLY store separately, because it needs to be reused by postesti
        dc_speckey_mpoly_default = {'compute_spec_key': compute_spec_key_esr3,
                                    'esti_spec_key': esti_spec_key_esr3,
                                    'moment_key': None,
                                    'momset_key': momset_key}

        # generate args
        dc_invoke_main_kwargs = {'speckey': param_compestispecs.get_speckey_string(**dc_speckey_default),
                                 'ge': bl_ge,
                                 'multiprocess': multiprocess,
                                 'estimate': estimate,
                                 'graph_panda_list_name': graph_panda_list_name_esr1,
                                 'save_directory_main': save_directory_main,
                                 'logging_level': logging.WARNING,
                                 'log_file': log_file,
                                 'log_file_suffix': ''}

        # Kwargs for combine_indi_esti
        dc_search_combine_indi_esti_kwargs = {'moment_key': dc_speckey_default['moment_key'],
                                              'momset_key': dc_speckey_default['momset_key'],
                                              'exo_or_endo_graph_row_select': exo_or_endo_graph_row_select,
                                              'image_save_name_prefix': 'AGG_ALLESTI_',
                                              'search_directory': None,
                                              'fils_search_str': None,
                                              'save_file_name': None,
                                              'save_panda_all': True,
                                              'graph_list': None,
                                              'top_estimates_keep_count': 2}
        """
        Step 1,2
        """
        # Update compute and esti specs
        for it_step in ar_steps:

            if it_step == 1 or it_step == 2:
                dc_speckey_default['compute_spec_key'] = compute_spec_key_esr1
                dc_speckey_default['esti_spec_key'] = esti_spec_key_esr1
                top_estimates_keep_count = top_estimates_keep_count_esr2

            if it_step == 3 or it_step == 4:
                dc_speckey_default = deepcopy(dc_speckey_mpoly_default)
                top_estimates_keep_count = top_estimates_keep_count_esr4

            if it_step == 5 or it_step == 6:
                dc_speckey_default['compute_spec_key'] = compute_spec_key_esr5
                dc_speckey_default['esti_spec_key'] = esti_spec_key_esr5
                top_estimates_keep_count = top_estimates_keep_count_esr6

            if it_step == 7 or it_step == 8:
                dc_speckey_default['compute_spec_key'] = compute_spec_key_esr7
                dc_speckey_default['esti_spec_key'] = esti_spec_key_esr7
                top_estimates_keep_count = top_estimates_keep_count_esr8

            """
            Estimatate and Simulate
            """
            if it_step == 1 or it_step == 3 or it_step == 5 or it_step == 7:
                for st_regions in ar_regions:

                    # A. combo_type and kwargs for invoke_main
                    combo_type = dc_combo_type[st_regions]
                    # update moment_key region-specific
                    dc_speckey_default['moment_key'] = dc_moment_key[st_regions]
                    # update spec-key, region specific and esti and compute spec specifics
                    dc_invoke_main_kwargs['speckey'] = dc_speckey_default

                    # B. MPOLY estimation before and after loops
                    # Determine esr esti/simu loop seed/start points
                    if it_step in [1, 3]:
                        # [['e', '20201025x_esr_mlt_all_beta', ['esti_param.beta'], None]]
                        # Number of points to randomly draw and estimate with one iteration at
                        # moment_key and momset_keys are parameters for estimate_set, they do not matter
                        dc_estispec = estispec.estimate_set(dc_speckey_default['esti_spec_key'])
                        esti_param_vec_count = dc_estispec['esti_param_vec_count']
                        ls_esr_start_loop = range(esti_param_vec_count)
                    elif it_step in [5, 7]:
                        ls_esr_start_loop = ls_it_esti_top_which
                        dc_speckey_mpoly_default['moment_key'] = dc_moment_key[st_regions]
                        compesti_short_name_mpoly = hardstring.gen_compesti_short_name(**dc_speckey_mpoly_default)
                    else:
                        raise ValueError(f'{it_step=} must be 1, 3, 5 or 7')

                    # C. Loop and run estimation and simulation
                    for it_esti_ctr in ls_esr_start_loop:

                        # D. Update combo_type
                        # D1. Simulation randomly and MPOLY approximation estimation
                        if it_step in [1, 3]:
                            combo_type[3] = it_esti_ctr
                        # D2. Simulate at MPOLY best, and estimate model using MPOLY as seeds
                        if it_step in [5, 7]:
                            combo_type[3] = 0
                            combo_type_e = parsecombotype.parse_combo_type_e(
                                compesti_short_name=compesti_short_name_mpoly,
                                esti_top_which=it_esti_ctr)
                            if len(combo_type) == 5:
                                combo_type[4] = combo_type_e
                            else:
                                combo_type.append(combo_type_e)

                        # E. Estimate and Simulate the Model
                        # try:
                        invoke_run_main.invoke_main(combo_type, **dc_invoke_main_kwargs)
                        # except Exception:
                        logging.critical(f'Finished this {it_esti_ctr=} of {len(ls_esr_start_loop)=}')

            """
            Step 2, Gather individual folder CSVs together, aggregate Excel with all simulations
            """
            if it_step == 2 or it_step == 4 or it_step == 6 or it_step == 8:
                for st_regions in ar_regions:
                    combo_type = dc_combo_type[st_regions]
                    search_directory = os.path.join(proj_sys_sup.main_directory(), 'esti',
                                                    combo_type[0] + '_' + combo_type[1], '')
                    dc_search_combine_indi_esti_kwargs['search_directory'] = search_directory
                    dc_search_combine_indi_esti_kwargs['moment_key'] = dc_moment_key[st_regions]
                    dc_search_combine_indi_esti_kwargs['compute_spec_key'] = dc_speckey_default['compute_spec_key']
                    dc_search_combine_indi_esti_kwargs['top_estimates_keep_count'] = top_estimates_keep_count

                    esticomp.search_combine_indi_esti(dc_paramstr_key_list_str[st_regions], combo_type_list_ab,
                                                      combo_type_list_date,
                                                      dc_speckey_default['esti_spec_key'],
                                                      **dc_search_combine_indi_esti_kwargs)

        # """
        # Step 3, MPOLY estimation with MPOLY surface from ..._mpoly_reg_coef.csv files
        # """
        # if any(item in [3, 4] for item in ar_steps):
        #
        #     # ESTI_SPEC_KEY_ESR1 and ESTI_SPEC_KEY_ESR3 share the same ESTI_PARAM_VEC_COUNT
        #     dc_speckey_default['compute_spec_key'] = compute_spec_key_esr3
        #     dc_speckey_default['esti_spec_key'] = esti_spec_key_esr3
        #
        #     # generate args
        #     dc_invoke_main_kwargs['graph_panda_list_name'] = graph_panda_list_name_esr3
        #
        #     if 3 in ar_steps:
        #
        #         for st_regions in ar_regions:
        #             combo_type = dc_combo_type[st_regions]
        #             dc_speckey_default['moment_key'] = dc_moment_key[st_regions]
        #             # update spec-key, region specific and esti and compute spec specifics
        #             dc_invoke_main_kwargs['speckey'] = dc_speckey_default
        #
        #             dc_estispec = estispec.estimate_set(dc_speckey_default['esti_spec_key'])
        #             esti_param_vec_count = dc_estispec['esti_param_vec_count']
        #
        #             for it_esti_ctr in range(esti_param_vec_count):
        #                 # Update the 3rd element of combo_type, which determines which draw index to use
        #                 combo_type[3] = it_esti_ctr
        #                 try:
        #                     invoke_run_main.invoke_main(combo_type, **dc_invoke_main_kwargs)
        #                 except Exception:
        #                     logging.critical(f'Finished this {it_esti_ctr=} of {range(esti_param_vec_count)=}')
        #
        #     if 4 in ar_steps:
        #
        #         for st_regions in ar_regions:
        #             # identical to step 2 earlier
        #             combo_type = dc_combo_type[st_regions]
        #             search_directory = os.path.join(proj_sys_sup.main_directory(), 'esti', combo_type[0] + '_' + combo_type[1], '')
        #             dc_search_combine_indi_esti_kwargs['search_directory'] = search_directory
        #             dc_search_combine_indi_esti_kwargs['moment_key'] = dc_moment_key[st_regions]
        #
        #             esticomp.search_combine_indi_esti(dc_paramstr_key_list_str[st_regions], combo_type_list_ab, combo_type_list_date,
        #                                               dc_speckey_default['esti_spec_key'],
        #                                               **dc_search_combine_indi_esti_kwargs)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
