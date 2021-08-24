'''
Created on Apr 8, 2018

@author: fan
'''

import sys
sys.path.append('c:\\Users\\fan\\PyFan\\ProjectSupport')
sys.path.append('c:\\Users\\fan\\ThaiJMP')

import projectsupport.systemsupport as proj_sys_sup
import os
import pdflatexetc.jinja_template as jinja_template
import projectsupport.systemsupport as proj_sys_sup
import projectsupport.hardcode.string_shared as hardstring
import parameters.model.a_model as param_model_a
import json
import ast
import pandas as pd

# folder = 'C:/Users/fan/ThaiJMP/parameters/json/c_201809/'
# file = 'c_20180901_list_tKap_mlt.json'
# file_path = folder + file
# json_out = proj_sys_sup.load_json(file_name_and_directory=file_path)

simulate_csv_directory = 'C:/Users/fan/Documents/Dropbox (UH-ECON)/Project Dissertation/simu/b_20180904x_ITG_kapp/'
simulate_csv_directory = 'C:/Users/fan/Documents/Dropbox (UH-ECON)/Project Dissertation/simu/b_c_20180901_list_tall_mlt_ne1a2_JSON_I6_fcfb/'

simulate_csv_file_name = '20180904x_ITG_kapp_endo'
simulate_csv_file_name = 'c_20180901_list_tall_mlt_ne1a2_JSON_I6_fcfb_endo'

simulate_csv_file_name_for_stata = simulate_csv_file_name + '_ctr3d'
for_stata_save_file_name = simulate_csv_directory + simulate_csv_file_name_for_stata + '.csv'

current_policy_column = 'esti_param.kappa'
current_policy_column = 'esti_param.BNF_BORR_P'


file_path = simulate_csv_directory + simulate_csv_file_name + '.csv'
simu_df = proj_sys_sup.read_csv(csv_file_folder=file_path)
print(simu_df.shape)

'''
1. Include Only Wgt Main Results
'''
exo_or_endo_graph_row_select = '_exo_wgtJ'
exo_or_endo_graph_row_select = '_equitg_wgtJitg'
exo_or_endo_graph_row_select = '_equ_wgtJ'

simu_df = simu_df[simu_df['file_save_suffix'].str.contains(exo_or_endo_graph_row_select)==True]
print(simu_df.shape)
print(list(simu_df.columns))

'''
2. Obtain columns for credit market choices
'''
steady_agg_suffixes = hardstring.steady_aggregate_suffixes()
steady_var_suffixes_dict = hardstring.get_steady_var_suffixes()
translate_jinja_name = param_model_a.choice_index_names()['translate_jinja_name']
moment_csv_strs = hardstring.moment_csv_strs()

choice_set_list = simu_df['model_option.choice_set_list'].iloc[0]
choice_set_list = ast.literal_eval(choice_set_list)
choice_names_use = simu_df['model_option.choice_names_use'].iloc[0]
choice_names_use = ast.literal_eval(choice_names_use)

pf_col_name_dict = {}
for ctr, j in enumerate(choice_set_list):
    jinja_j =  translate_jinja_name[j]
    pf_col_name = choice_names_use[ctr] + '_' + \
                    steady_var_suffixes_dict['probJ_opti_grid'] + \
                    steady_agg_suffixes['_j_agg'][0]
    pf_col_name_dict[jinja_j] = pf_col_name

print(pf_col_name_dict)

'''
3. Add add probabilities to go from 7 to 4
'''
shr_inf = simu_df[pf_col_name_dict['IB']] + simu_df[pf_col_name_dict['IS']]
shr_for = simu_df[pf_col_name_dict['FB']] + simu_df[pf_col_name_dict['FS']]
shr_joint = simu_df[pf_col_name_dict['FBIB']] + simu_df[pf_col_name_dict['FBIS']]
shr_none_m_avg = simu_df[pf_col_name_dict['NONE']]

# shr_joint =
# shr_none_m_avg =

'''
4. Include Interest Rate Column and other column names
'''
R_INFORM = simu_df[moment_csv_strs['R_INFORM'][1]]
BNF_SAVE_P = simu_df[moment_csv_strs['BNF_SAVE_P'][1]]
BNF_BORR_P = simu_df[moment_csv_strs['BNF_BORR_P'][1]]
kappa = simu_df[moment_csv_strs['kappa'][1]]
R_FORMAL_SAVE = simu_df[moment_csv_strs['R_FORMAL_SAVE'][1]]
R_FORMAL_BORR = simu_df[moment_csv_strs['R_FORMAL_BORR'][1]]

'''
5. Export: converting to stata do file graphing variable names
'''
simu_df['shr_inf'] = pd.Series(shr_inf, index=simu_df.index)
simu_df['shr_for'] = pd.Series(shr_for, index=simu_df.index)
simu_df['shr_joint'] = pd.Series(shr_joint, index=simu_df.index)
simu_df['shr_none_m_avg'] = pd.Series(shr_none_m_avg, index=simu_df.index)
simu_df['interestinf'] = pd.Series(R_INFORM, index=simu_df.index)

simu_df['bnf_save_p_r1'] = pd.Series(BNF_SAVE_P, index=simu_df.index)
simu_df['bnf_borr_p_r1'] = pd.Series(BNF_BORR_P, index=simu_df.index)
simu_df['kappa_r1'] = pd.Series(kappa, index=simu_df.index)
simu_df['int_formal_save'] = pd.Series(R_FORMAL_SAVE, index=simu_df.index)
simu_df['int_formal_borr'] = pd.Series(R_FORMAL_BORR, index=simu_df.index)

'''
6. Export
'''
varkeep_list = ['bnf_save_p_r1', 'bnf_borr_p_r1', 'kappa_r1', 'int_formal_save', 'int_formal_borr',
                'interestinf', 'shr_inf', 'shr_for', 'shr_joint', 'shr_none_m_avg']

if (current_policy_column in varkeep_list):
    pass
else:
    varkeep_list.insert(0, current_policy_column)
    print(varkeep_list)

counter_3dims = simu_df[varkeep_list]
proj_sys_sup.save_panda(for_stata_save_file_name, counter_3dims)

