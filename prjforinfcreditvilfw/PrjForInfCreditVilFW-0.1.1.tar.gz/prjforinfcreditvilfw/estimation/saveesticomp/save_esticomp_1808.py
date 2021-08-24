'''
Created on Aug 16, 2018

@author: fan
'''

import estimation.postprocess.process_main as esticomp

def esti_comp_20180816():
    
    paramstr_key_list = ['list_policy_Kap_1and2'] 
    combo_type_list_ab = 'c'
    combo_type_list_date = '20180815x'
    esti_spec_key = 'kap_m0_nld_m'
    search_directory_main = 'C:/Users/fan/Documents/Dropbox (UH-ECON)/Project Dissertation EC2/thaijmp201808j7itgesti/esti/'
    search_directory = search_directory_main + combo_type_list_ab + \
                        '_' + combo_type_list_date + \
                        '_' + paramstr_key_list[0] + '/'  
    
    
    esticomp.search_combine_indi_esti(
                            paramstr_key_list,
                            combo_type_list_ab,
                            combo_type_list_date, esti_spec_key,
                            moment_key=0, momset_key=1,
                            exo_or_endo_graph_row_select = '_exo_wgtJ',
                            image_save_name_prefix = 'AGG_ALLESTI_', 
                            search_directory = search_directory,
                            fils_search_str = None, 
                            save_file_name = None, 
                            save_panda_all = True,
                            graph_list = None,
                            top_estimates_keep_count = 4)



if __name__ == "__main__":
    esti_comp_20180816()