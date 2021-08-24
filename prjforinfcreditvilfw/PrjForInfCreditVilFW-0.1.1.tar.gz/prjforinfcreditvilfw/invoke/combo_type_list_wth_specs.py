'''
Created on Jun 9, 2018

@author: fan
'''

import parameters.loop_combo_type_list.param_combo_type_list as paramcombotypelist
import parameters.runspecs.compute_specs as computespec


def gen_combo_type_list(gn_invoke_set=1, fargate=False, paramstr_key_list=None,
                        combo_type_list_ab='a', combo_type_list_date='20180607',
                        combo_list_subset=None):
    """
        
    Parameters
    ----------
    combo_list_subset: list of int
        [0,1,2], [0], [3], [5,6] etc
        
    """

    '''cpu and memory none for fargate means use what is specified in spedificiation for each speckey'''
    vcpus = None
    cpu = None
    memory = None

    """
    invoke_set the same for farget and local.
    """
    bl_is_str = isinstance(gn_invoke_set, str)
    bl_is_int = isinstance(gn_invoke_set, int)
    if bl_is_int:
        bl_it_between = (1 <= gn_invoke_set <= 11)
    else:
        bl_it_between = False

    if bl_it_between:
        speckey = computespec.get_speckey_dict(gn_invoke_set)
    elif bl_is_str:
        speckey = gn_invoke_set
    else:
        pass

    if bl_it_between or bl_is_str:

        if (paramstr_key_list is None):
            # None means do not loop over parameter
            paramstr_key_list = ['']

            # If specify anything, loop over parameter
            paramstr_key_list = ['K_DEPRECIATION']
        #             paramstr_key_list = ['BNI_BORR_P']
        else:
            #             use list specified externally
            pass

        if (paramstr_key_list == ['']):
            '''
            grid_param.len_k_start below because in panda_param_loop, need to 
            sort by combo_type[2], there is only one row, so sorting not needed.  
            '''
            combo_type_list = [[combo_type_list_ab,
                                combo_type_list_date,
                                None,
                                None]]
        else:
            combo_type_list = paramcombotypelist.gen_combo_type_list(combo_type_list_ab,
                                                                     combo_type_list_date,
                                                                     paramstr_key_list)
    else:
        pass

    return speckey, vcpus, cpu, memory, combo_type_list


def gen_combo_type_list_old(invoke_set=0, combo_type_list_ab='a', combo_type_list_date='20180607'):
    """
        combo_type_list = \
        [
            ['a', '20180607_alpk', 'esti_param.alpha_k']
            ['a', '20180517_A', 'data_param.A']
            ['a', '20180403a', 'NA']
        ]
        
        Parameters
        ----------
        combo_type_list_ab: string
            a or b or other strings
            for combo type string, not for the parameter categories
            in combo.py, choose to go to combo_list_a or combo_list_b_FC for example
        combo_type_list_date: string date
            for combo type string, not fo the parameter cataegories
            date with year month and day
            this is for combo_list_b_FC for example, 
             
    """

    '''cpu and memory none for fargate means use what is specified in spedificiation for each speckey'''

    cpu = None
    memory = None
    #     cpu = str(1024*1)
    #     memory = str(1024*10)

    if (invoke_set == 1):
        """
        local xps
        not ge
        sequential or parallel
        small run testing
            all parameters
        """

        speckey = 'l-ng-s-x'
        #         speckey = 'l-ng-p-x'

        paramstr_key_list = None
        paramstr_key_list = ['beta']
        #         paramstr_key_list = ['data__A_params_mu']
        #         paramstr_key_list = 'reg_memory_main'
        combo_type_list = paramcombotypelist.gen_combo_type_list(combo_type_list_ab,
                                                                 combo_type_list_date,
                                                                 paramstr_key_list)
    if (invoke_set == 2):
        """
        local xps
        ge
        sequential or parallel
        small run testing
            all parameters
        """

        #         speckey = 'l-ge-s-x'
        speckey = 'l-ge-p-x'

        paramstr_key_list = None
        paramstr_key_list = ['A']
        #         paramstr_key_list = ['data__A_params_mu']
        combo_type_list = paramcombotypelist.gen_combo_type_list(combo_type_list_ab,
                                                                 combo_type_list_date,
                                                                 paramstr_key_list)

    """
    FARGATE
    """

    if (invoke_set == 101):
        """
        fargate
        no general equilibrium
        sequential
        large
            regular memory parameters
        """
        speckey = 'f-ng-s-d'
        paramstr_key_list = 'reg_memory'
        #         paramstr_key_list = ['maxinter']
        combo_type_list = paramcombotypelist.gen_combo_type_list(combo_type_list_ab,
                                                                 combo_type_list_date,
                                                                 paramstr_key_list)

    if (invoke_set == 102):
        """
        fargate
        no general equilibrium
        sequential
        large
            big memory parameters
        """
        speckey = 'f-ng-s-d'
        paramstr_key_list = 'big_memory'
        cpu = str(1024 * 4)
        memory = str(1024 * 30)
        #         paramstr_key_list = ['len_choices']
        combo_type_list = paramcombotypelist.gen_combo_type_list(combo_type_list_ab,
                                                                 combo_type_list_date,
                                                                 paramstr_key_list)

    if (invoke_set == 103):
        """
        parallel run of no ge 101
        """
        speckey = 'f-ng-p-d'
        paramstr_key_list = 'reg_memory_itg'
        #         paramstr_key_list = ['len_choices']
        combo_type_list = paramcombotypelist.gen_combo_type_list(combo_type_list_ab,
                                                                 combo_type_list_date,
                                                                 paramstr_key_list)

    if (invoke_set == 111):
        """
        fargate
        general equilibrium
        parallel
        test
        """
        speckey = 'f-ge-p-x'
        #         paramstr_key_list = ['maxinter']
        paramstr_key_list = 'reg_memory'
        combo_type_list = paramcombotypelist.gen_combo_type_list(combo_type_list_ab,
                                                                 combo_type_list_date,
                                                                 paramstr_key_list)
    if (invoke_set == 112):
        """
        fargate
        general equilibrium
        parallel
        medium
        """
        speckey = 'f-ge-p-z'
        #         paramstr_key_list = ['maxinter']
        paramstr_key_list = 'reg_memory'
        paramstr_key_list = 'reg_memory_itg'
        combo_type_list = paramcombotypelist.gen_combo_type_list(combo_type_list_ab,
                                                                 combo_type_list_date,
                                                                 paramstr_key_list)
    if (invoke_set == 113):
        """
        fargate
        general equilibrium
        parallel
        big  
        """
        speckey = 'f-ge-p-d'
        #         paramstr_key_list = ['maxinter']
        paramstr_key_list = 'reg_memory'
        combo_type_list = paramcombotypelist.gen_combo_type_list(combo_type_list_ab,
                                                                 combo_type_list_date,
                                                                 paramstr_key_list)

    if (invoke_set == 114):
        """
        fargate
        general equilibrium
        sequential
        large
            alll parameters
            time:
                + len_choices = 2086s
                    + (0.0506*4 + 0.0127*16)*(2086/(60*60)) = 0.235 
                + len_states = 1233s
                    + (0.0506*4 + 0.0127*16)*(1233/(60*60)) = 0.139
        """
        speckey = 'f-ge-p-d'
        paramstr_key_list = 'big_memory'
        paramstr_key_list = 'reg_memory_itg'
        cpu = str(1024 * 4)
        memory = str(1024 * 16)
        #         paramstr_key_list = ['len_choices']
        combo_list = paramcombotypelist.gen_combo_type_list(combo_type_list_ab,
                                                            combo_type_list_date,
                                                            paramstr_key_list)

    return speckey, cpu, memory, combo_type_list
