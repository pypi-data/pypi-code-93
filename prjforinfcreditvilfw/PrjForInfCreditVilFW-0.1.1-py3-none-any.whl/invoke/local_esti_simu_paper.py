'''
Created on Sep 9, 2018

full local run process

@author: fan
'''
import time
import projectsupport.hardcode.string_shared as hardstring

import invoke.local_estimate as invoke_esti
import invoke.run_estimate_aws_globsumm as estimanage
import invoke.local_simulate as localsimu

import estimation.postprocess.jsoncsv.gen_counter_3dims_data as gen_counter3dims

import parameters.loop_combo_type_list.param_str as paramloopstr
import projectsupport.systemsupport as proj_sys_sup
import invoke.combo_type_list_wth_specs as paramcombospecs
import parameters.runspecs.compute_specs as computespec
import subprocess as sp
import boto3aws.run_aws as runfargate
import _paper.genpdf as genpdf

def run_esti_simu_paper(
        invoke_local_fargate = 'local',
        sync_ecs = True,
        run_step = 1,
        invoke_set_esti = 1,
        sync_glob_summ_type = 'glob',
        esti_list = ['ce', 'ne'],
        paramstr_key_list_prefix = 'list_tall', 
        key_simu_list = ['R_FORMAL_BORR','R_FORMAL_SAVE',
                         'BNF_BORR_P','BNF_SAVE_P',
                         'kappa'],
        combo_type_list_ab_esti = 'c',
        combo_type_list_ab_simu = 'b',
        combo_type_list_date = '20180901',
        esti_spec_key_root = 'esti_test',
        esti_spec_key_suffix_local_list = ['_11'],
        momset_key = 4,
        moment_key_ce = 3, 
        moment_key_ne = 4,
        GE_list = [3],
        save_directory_main_esti = 'esti',
        save_directory_main_simu = 'simu'):
    """
    Have to create program for run, otherwise, can not use multiprocessing. 
    run into freeze_support() errors
    in windows, all multiprocessing have to be invoked protected by main:
        https://stackoverflow.com/questions/24374288/where-to-put-freeze-support-in-a-python-script
    """
    '''
    Step 0a
    Main Invokes
    '''
    run_step_1 = False
    run_step_2 = False
    run_step_3 = False
    run_step_4 = False
    run_step_5 = False
    run_step_6 = False
    run_step_7 = False
    if (run_step == 1):
        run_step_1 = True
    elif (run_step == 2):
        run_step_2 = True
    elif (run_step == 3):
        run_step_3 = True
    elif (run_step == 4):    
        run_step_4 = True
    elif (run_step == 5):    
        run_step_5 = True
    elif (run_step == 6):    
        run_step_6 = True
    elif (run_step == 7):    
        run_step_7 = True
    else:
        raise('not possible')
    
    force_integrate_simu_countner = False
#     if (esti_list is None):
#         esti_list = ['ce', 'ne']
#     GE_list = [3]
#     esti_list = ['ne']
#     esti_list = ['ce']
    
    '''
    Step 0b
    Main Parameters
    '''
    region_time_suffix = hardstring.region_time_suffix()
    moment_key_dict = {'ne':moment_key_ne,
                       'ce':moment_key_ce}                    
    paramstr_key_list_dict = {'ne': [paramstr_key_list_prefix + region_time_suffix['_ne1a2'][0]],
                              'ce': [paramstr_key_list_prefix + region_time_suffix['_ce1a2'][0]],
                              'all': [paramstr_key_list_prefix]}
    region_time_suffix_dict = {'ne': [region_time_suffix['_ne1a2'][0]],
                               'ce': [region_time_suffix['_ce1a2'][0]],
                               'all': [paramstr_key_list_prefix]}
    
    paramstr_key_list_dict_simu = {}    
#     if (key_simu_list is None):
#         key_simu_list_more = ['BNI_LEND_P','BNI_BORR_P']
#         key_simu_list = ['R_FORMAL_BORR','R_FORMAL_SAVE',
#                         'BNF_BORR_P','BNF_SAVE_P',
#                         'kappa']
        
#         key_simu_list = ['R_FORMAL_BORR','R_FORMAL_SAVE']
#         key_simu_list = ['BNF_BORR_P','BNF_SAVE_P']
#         key_simu_list = ['kappa']
#         
#         key_simu_list = ['R_FORMAL_BORR']
#         key_simu_list = ['R_FORMAL_SAVE']
#         key_simu_list = ['BNF_BORR_P']    
#         key_simu_list = ['BNF_SAVE_P']
#         key_simu_list = ['kappa']
    
    for nece in ['ne', 'ce']:
        if (nece == 'ne'):
            suffix = hardstring.peristr(period=hardstring.region_time_dict()['ne1'][1])
        if (nece == 'ce'):
            suffix = hardstring.peristr(period=hardstring.region_time_dict()['ce1'][1])
    
        cur_list = []
        if (key_simu_list is not None):
            for key_simu in key_simu_list:
                cur_list.append(key_simu + suffix)    
            paramstr_key_list_dict_simu[nece] = cur_list
    
    '''
    STEP 0
    Update Docker
    '''
    if ((invoke_local_fargate in ['fargate', 'Spot', 'OnDemand']) 
        and
        (sync_ecs == True)
        and 
        (run_step_1 or run_step_4)):
        '''
        run_step_1 needs to update docker because it is pushing new codes potentially
        run_step_4 MUST update docker because it should have new estimates in JSON that needs to be pushed out
        '''
        runfargate.update_docker()
    
    '''
    STEP 1
    Local estimate
    '''
    if (run_step_1):
#         invoke = 'local'
        invoke = invoke_local_fargate
        sync_ecs = True
        
#         invoke_set = 1
#         esti_spec_key = esti_spec_key_root + esti_spec_key_suffix_local

        invoke_set_esti = 1
        if ('_ITG' in combo_type_list_date):
            invoke_set_esti = 4
        if (esti_spec_key_root == 'esti_mpoly'):
            # only for estimate, not for simulate
            invoke_set_esti = 0 # mpoly_1
            
        if (esti_list is None):    
            esti_list = ['ne']
            esti_list = ['ce']
        for cur_esti in esti_list:
            for esti_spec_key_suffix_local in esti_spec_key_suffix_local_list:
                esti_spec_key = esti_spec_key_root + esti_spec_key_suffix_local
                paramstr_key_list = paramstr_key_list_dict[cur_esti]
                moment_key = moment_key_dict[cur_esti]
                invoke_esti.estimate(invoke, invoke_set_esti, sync_ecs = False,
                                     esti_spec_key = esti_spec_key,
                                     combo_type_list_ab = combo_type_list_ab_esti, combo_type_list_date = combo_type_list_date,
                                     paramstr_key_list = paramstr_key_list,
                                     moment_key = moment_key, momset_key = momset_key)
        
    
    '''
    STEP 2
    Local Folder copy over to EC2, manual:
        from: C:/Users/fan/Documents/Dropbox (UH-ECON)/Project Dissertation/esti
            - c_20180901_list_tall_mlt_ce1a2
            - c_20180901_list_tall_mlt_ne1a2
        to: C:/Users/fan/Documents/Dropbox (UH-ECON)/Project Dissertation EC2/thaijmp201808j8var/esti
    '''
    
    '''
    STEP 3
    glob etc
    Moving and combining Tex, DO, and json files 
    4. Move to dropbox
        + move tex, do, json
        + copy json files for ne ce earlier period to
            - \parameters\json\..        
    '''
    if (run_step_2 or run_step_3 or run_step_4):
        region_time_suffix = hardstring.region_time_suffix()
        esti_setting_dict = {}        
        esti_setting_dict['integrated'] = False
        # esti_setting_dict['exo_or_endo_graph_row_select'] = '_exo_wgtJ'
        esti_setting_dict['exo_or_endo_graph_row_select'] = hardstring.file_suffix(file_type='json', sub_type='partial', integrated=False)
        if ('_ITG' in combo_type_list_date):
            '''This is important, need to have this boolean for integration related things
            but this means later codes in sync will add ITG, so drop ITG from string here
            a conversion, convert _ITG to this boolean, which gives _ITG back later
            '''
            esti_setting_dict['integrated'] = True
            # esti_setting_dict['exo_or_endo_graph_row_select'] = '_exoitg_wgtJitg'                       
            esti_setting_dict['exo_or_endo_graph_row_select'] = hardstring.file_suffix(file_type='json', sub_type='partial', integrated=True)
            combo_type_list_date = combo_type_list_date.replace('_ITG', '')
        esti_setting_dict['esti_combo_type_list_ab'] = combo_type_list_ab_esti
        esti_setting_dict['esti_combo_type_list_date'] = combo_type_list_date
        esti_setting_dict['esti_save_directory_main'] = 'esti'            
        esti_setting_dict['momset_key'] = momset_key        
        
        if (combo_type_list_date.endswith('x') or 'x_' in combo_type_list_date):
            '''if specify more, becomes xx, already specified above'''
            run_size = ''
        elif (combo_type_list_date.endswith('d') or 'd_' in combo_type_list_date):
            '''already specified above'''
            run_size = ''
        else:
            run_size = ''
        
        if (esti_list is None):
            esti_list = ['ne']
            esti_list = ['ce']
        
#         run_type = 'glob' # first step
    #     run_type = 'gentopsumm' # future runs
        for esti_obj_rank_tex_pdf in reversed(range(200)):                            
            for cur_esti in esti_list:
                paramstr_key_list = paramstr_key_list_dict[cur_esti]
                esti_setting_dict['moment_key'] = moment_key_dict[cur_esti]
                esti_setting_dict['esti_obj_rank_tex_pdf'] = esti_obj_rank_tex_pdf
                esti_setting_dict['top_estimates_keep_count'] = max(esti_obj_rank_tex_pdf+1, 5)
                estimanage.esti_glob_summ(paramstr_key_list = paramstr_key_list,
                                           run_size = run_size,
                                           esti_spec_key_root = esti_spec_key_root,
                                           run_type=sync_glob_summ_type,
                                           sync_ecs_init = True, 
                                           **esti_setting_dict)            
            '''
            Generate PDF to be stored in: 
                C:/Users/fan/Documents/Dropbox (UH-ECON)/Project Dissertation/paper/draft/sec_tabfig/
            '''
            genpdf.gen_paper_draft(update_file_list = [7],
                                   timestamp_type = 1,
                                   file_suffix = '_' + combo_type_list_date + 'R' + str(esti_obj_rank_tex_pdf),
                                   start_viewer = False)
                    
    
    '''
    Step 4 and 5 and 6 Simulate
    '''
    if (run_step_5 or run_step_6 or run_step_7):
#         invoke = 'local'
        invoke = invoke_local_fargate        
        sync_ecs = False
        
    #     force_integrate_simu_countner = False
        simu_force_add_ITG = ''
        if ('_ITG' in combo_type_list_date):
            'has ITG'
            pass
        else:
            if (force_integrate_simu_countner):
                simu_force_add_ITG = '_ITG'
        
    #     regardless of how estimation was done, here should make ITG and not ITG GE. and Partial Results    
        '''
        date uses esti so resulting full name would be
        b_c_20180901 for example, show where the estimation is coming from
        ''' 
        combo_type_list_ab_date = hardstring.combo_type_date_type_combine(combo_type_list_ab_esti, combo_type_list_date)
        for GE in GE_list:
            if (GE==0):
                # Testing, 3 POINTS, Partial
                if ('_ITG' in combo_type_list_date):
                    invoke_set = 2 # for integrated, 4 workers
                else:
                    invoke_set = 1 # for not integrated, 4 workers    
            if (GE==1):
                # Testing, 3 POINTS, GE
                if ('_ITG' in combo_type_list_date):
                    invoke_set = 5 # for integrated, 4 workers
                else:
                    invoke_set = 5 # for not integrated, 4 workers    
            if (GE==2):
                # Full Partial
                if ('_ITG' in combo_type_list_date):
                    invoke_set = 4 # for integrated
                else:
                    invoke_set = 4 # for not integrated    
            if (GE==3):
                # Full GE
                if ('_ITG' in combo_type_list_date):
                    invoke_set = 11 # for integrated, 4 workers
                else:
                    invoke_set = 6 # for not integrated, 4 workers    
            
        #     esti_spec_key_for_simu = None
    #     esti_spec_key_for_simu = 'kap_m0_nld_m_simu'
        esti_spec_key_for_simu = esti_spec_key_root + '_11_simu'
        
        if (esti_list is None):
            esti_list = ['ne']
            esti_list = ['ce']
            
        for cur_esti in esti_list:
            combo_type_list_date_use = combo_type_list_ab_date + '_' + paramstr_key_list_dict[cur_esti][0] + \
                                        '_JSON' + simu_force_add_ITG + '_I' + str(invoke_set)
                                        
            paramstr_key_list = paramstr_key_list_dict_simu[cur_esti]
            paramstr_key_list = key_simu_list 
            moment_key = moment_key_dict[cur_esti]        
            
            if (run_step_5):
                '''
                5. Run Files
                    + run simulate            
                '''
                localsimu.manage_local_farge(
                            invoke = invoke,
                            sync_ecs = False,
                            combo_type_list_ab = combo_type_list_ab_simu,
                            combo_type_list_date = combo_type_list_date_use,
                            invoke_set = invoke_set,
                            esti_spec_key_for_simu = esti_spec_key_for_simu,
                            save_directory_main = save_directory_main_simu,
                            moment_key = moment_key,
                            momset_key = momset_key,
                            paramstr_key_list = paramstr_key_list)
            
            if (run_step_6):
                
                esti_setting_dict = {}
                esti_setting_dict['simu_combo_type_list_ab'] = combo_type_list_ab_simu
                esti_setting_dict['simu_combo_type_list_date'] = combo_type_list_date_use
                esti_setting_dict['simu_save_directory_main'] = 'simu'
                esti_setting_dict['integrated'] = False
                if ('_ITG' in combo_type_list_date):
                    esti_setting_dict['integrated'] = True                    
#                     combo_type_list_date = combo_type_list_date.replace('_ITG', '')
                    
                esti_setting_dict['momset_key'] = momset_key        
                
                if (combo_type_list_date.endswith('x') or 'x_' in combo_type_list_date):
                    '''if specify more, becomes xx, already specified above'''
                    run_size = ''
                elif (combo_type_list_date.endswith('d') or 'd_' in combo_type_list_date):
                    '''already specified above'''
                    run_size = ''
                else:
                    run_size = ''
                
                if (esti_list is None):
                    esti_list = ['ne']
                    esti_list = ['ce']
                
                
                for cur_esti in esti_list:                        
                    esti_setting_dict['esti_obj_rank_tex_pdf'] = esti_obj_rank_tex_pdf

                    # paramstr_key_list ['R_FORMAL_BORR', 'R_FORMAL_SAVE', 'BNF_BORR_P', 'BNF_SAVE_P', 'kappa']
                    for paramstr_key in paramstr_key_list:
                        estimanage.esti_glob_summ(paramstr_key_list = [paramstr_key],
                                                   run_size = run_size,
                                                   esti_spec_key_root = esti_spec_key_root,
                                                   run_type=sync_glob_summ_type,
                                                   sync_ecs_init = False, 
                                                   **esti_setting_dict)
            
            
            if (run_step_7):
                '''
                + run latex on main draft file
                    - probability tables now match up to what is in tex preamble
                + run stata file:
                    - esti_fit_prob_j.do: generate probability match
                    - matches up to what is in the global do from both regions
                4. Copy files over to imgtab in draft folder
                    + copy to imgtab with date: \Project Dissertation\paper\imgtab\20180906a
                        - do
                        - tex
                        - pdf graph        
                5. Run draft file
                    + for do tex files, use what is in _paper folder in git
                    + for images, use what is in paper folder in project dropbox                                
                '''
                
                '''
                4b results are stored in simu_diretory
                '''
                fargate = False
                speckey, vcpus, cpu, memory, combo_type_list = \
                    paramcombospecs.gen_combo_type_list(invoke_set, fargate, paramstr_key_list,
                                                        combo_type_list_ab_simu, combo_type_list_date)
                cur_computespec = computespec.compute_set(compute_spec_key=speckey, fargate=False)
                computespec_ge = cur_computespec['ge']                
                
                pdf_list = []
                for param_key in paramstr_key_list:
                    
                    param_savestr = paramloopstr.param2str()[param_key][0]
                    param_group_name = paramloopstr.param2str()[param_key][1]
                    
                    '''
                    4b1, simulation folder
                    '''
                    sub_folder_name = hardstring.combo_type_date_type_combine(combo_type_list_ab_simu, combo_type_list_date_use) + param_savestr
                    if (invoke == 'local'):
                        simulate_csv_directory = proj_sys_sup.get_paths(main_folder_name = 'simu', sub_folder_name = sub_folder_name)
                    else:
                        simulate_csv_directory = proj_sys_sup.get_paths(main_folder_name = 's3local_simu', sub_folder_name = sub_folder_name)
                        
                    '''
                    4b2, simulation file name
                    '''                    
                    if (computespec_ge):
                        sub_type = 'equilibrium'
                    else:
                        sub_type = 'partial'
                    suffix = hardstring.file_suffix(file_type='csv', sub_type=sub_type)
                    simulate_csv_file_name = combo_type_list_date_use + param_savestr + suffix

                    '''
                    4b3, simulation select rows
                    '''
                    integrated = False
                    if ('_ITG' in combo_type_list_date):
                        integrated = True
                    exo_or_endo_graph_row_select = hardstring.file_suffix(file_type='json',
                                                                          sub_type=sub_type,
                                                                          integrated=integrated)
                    
                    '''
                    4b4, grab and gen counter file
                    '''
                    csv_name_suffix = '_ctr3d'
                    for_stata_save_file_directory_name = gen_counter3dims.gen_3dims_csv_fromcsv(
                                                        simulate_csv_file_name,
                                                        simulate_csv_directory,
                                                        current_policy_column = param_group_name,
                                                        exo_or_endo_graph_row_select = exo_or_endo_graph_row_select,
                                                        csv_name_suffix = csv_name_suffix)
                    stata_save_file_name = for_stata_save_file_directory_name.split('/')[-1]
                    
                    '''
                    5a. Moving Folder (simu 3dim counter aggregate folder):
                        b_c_20180901_list_tall_mlt_ce1a2_JSON_I6_fbrR/
                        b_c_20180901_list_tall_mlt_ce1a2_JSON_I6_fcfb/
                        ...
                        to
                        ...
                        b_c_20180901_list_tall_20180909/ aggregate both region 3 dim policy counterfactual csvs           
                    '''                    
                    non_region_specific_simuesti_directory, append_or_add, last_folder, \
                        last_folder_non_region_specific \
                        = hardstring.get_generic_folder(save_directory = for_stata_save_file_directory_name,
                                                        main_folder_name = 'simu')
                        
                    proj_sys_sup.copy_rename(for_stata_save_file_directory_name,
                                             non_region_specific_simuesti_directory + stata_save_file_name)

                    '''
                    5b. Moving Folder (simu 3dim counter aggregate folder):
                        from in simu folder:
                            b_c_20180901_list_tall_20180909/ aggregate both region 3 dim policy cunterfactual csvs           
                        to in draft folder:
                                b_c_20180901_list_tall_20180909/ identical
                            next to the estimation folder
                                c_20180901_list_tall_20180909/ identical                            
                    '''
                    paper_imgtab_directory = proj_sys_sup.get_paths('paper.imgtab', sub_folder_name = last_folder_non_region_specific)
                    proj_sys_sup.copy_rename(for_stata_save_file_directory_name,
                                             paper_imgtab_directory + stata_save_file_name)
                    
                    '''
                    5c. Moving Results to _draft folder, without region time specific information
                        c
                        b
                        _mlt_ce1a2
                        _fbrR
                        _equ_wgtJ
                    '''
                    _stata_draw_file_name = \
                        combo_type_list_ab_esti + \
                        '_' + combo_type_list_ab_simu + \
                        region_time_suffix_dict[cur_esti][0] + \
                        param_savestr + \
                        exo_or_endo_graph_row_select + \
                        csv_name_suffix
                    pdf_list.append(_stata_draw_file_name + '.pdf')
                    _stata_draw_file_name_csv = _stata_draw_file_name + '.csv'
                    stata_estisimu_data_directory = proj_sys_sup.get_paths_in_git('stata.estisimu_data')
                    proj_sys_sup.copy_rename(for_stata_save_file_directory_name,
                                             stata_estisimu_data_directory + _stata_draw_file_name_csv)

                    '''
                    6. Invoke Stata
                    '''
    #                 cmd.exe /c "C:/Program Files (x86)/Stata14/StataMP-64bit" -e do RegRegRegFunc.do
                    stata_estisimu_data = proj_sys_sup.get_paths_in_git('stata.graph.counter_3dims.do')
                    stata_exe_directory = proj_sys_sup.local_stata_exe_directory()
                    command_str = '"'+stata_exe_directory+'" -e do "'+stata_estisimu_data+'" ' \
                                    + ' ' + region_time_suffix_dict[cur_esti][0] \
                                    + ' ' + param_savestr \
                                    + ' ' + exo_or_endo_graph_row_select                                    
                    process = sp.Popen(command_str, shell=True,
                                       stdin=None, stdout=None, stderr=None, close_fds=True)
#                     process.wait()
                
                '''
                7. Move STATA Generated PDFS to simu and paper.imgtab
                '''
                time.sleep(20) 
                for cur_img_pdf in pdf_list:
                    cur_img_pdf_file_directory = stata_estisimu_data_directory + cur_img_pdf                  
                    
                    nxt_img_pdf_file_directory = non_region_specific_simuesti_directory + cur_img_pdf
                    proj_sys_sup.copy_rename(cur_img_pdf_file_directory, nxt_img_pdf_file_directory)
                    
                    nxt_img_pdf_file_directory = paper_imgtab_directory + cur_img_pdf
                    proj_sys_sup.copy_rename(cur_img_pdf_file_directory, nxt_img_pdf_file_directory)
                    
#                     os.remove(stata_estisimu_data_directory + cur_img_pdf)
                    
#                     if (update_compile_folder):                
#                         '''
#                         D. Results C file moving to _paper folder where tex can be compiled.
#                         '''
#                         next_folder_file = proj_sys_sup.get_paths_in_git(folder_aggregate_simu) + save_name + tex_do_suffix
#                         proj_sys_sup.copy_rename(tex_save_directory_name_combine, next_folder_file)
                    
        
        
# if __name__ == "__main__":
#     run_esti_simu_paper()
