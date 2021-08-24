'''
Created on Dec 16, 2017

@author: fan

copied over from Simulation.py previous JMP codes

used early previously in JMP, not used later after tics generated choices

'''


# def choiceSpaceRangeRand(self, kbf, max_round=1, cur_round=0,
#                        stateSpaceDrawCount=stateSpaceDrawCount,
#                        choice_grid_count=choice_grid_count,
#                        seed=340, IO=None, useExisting=True, printDetailSolution=False):
#     """
#         stateSpacePoints input:
#             choice set around actual choice for estimation, actual choice in estimation in "state-space" slot for soluvalue code
#             allow for same code to process both, mean choice, each row corresponds to a state, all are same in soluvalue
#     """
#
#     curMean_K_choice = kbf.mean_kapital
#     curMean_K_sd = kbf.std_kapital
#
#     curMean_B_choice = kbf.mean_netborrsave
#     curMean_B_sd = kbf.std_netborrsave
#
#
#     if (useExisting == True):
#         np.random.seed(seed)
#         normal1 = simuSup.stateSpacePoints().genNormalBase(choice_grid_count)
#         normal2 = simuSup.stateSpacePoints().genNormalBase(choice_grid_count)
#     if (useExisting == False):
#         normal1 = simuSup.stateSpacePoints().genNormalBase(choice_grid_count)
#         normal2 = simuSup.stateSpacePoints().genNormalBase(choice_grid_count)
#
#     '''
#     a, K and B choice Grid, same size for mean and standard deviation
#     '''
#     # K Choices
#     K_ChoicePoints = (curMean_K_choice + normal1 * curMean_K_sd)
#
#     # B Choices
#     B_ChoicePoints = (curMean_B_choice + normal2 * curMean_B_sd)
#
#
#     '''
#     b, K and B choice Grid, state size for mean, shock size for standard deviation
#     '''
#     K_Mean_statespace_span = np.repeat(curMean_K_choice, stateSpaceDrawCount)
#     K_Shock_points = (normal1 * curMean_K_sd)
#
#     B_Mean_statespace_span = np.repeat(curMean_B_choice, stateSpaceDrawCount)
#     B_Shock_points = (normal2 * curMean_B_sd)
#
#     if (printDetailSolution == True):
#         print '\n stateSpaceEmaxRand'
#         simuSup.stateSpacePoints().printDataSummary(K_ChoicePoints, 'K_ChoicePoints')
#         simuSup.stateSpacePoints().printDataSummary(B_ChoicePoints, 'B_ChoicePoints')
#
#         simuSup.stateSpacePoints().printDataSummary(K_Mean_statespace_span, 'K_Mean_statespace_span')
#         simuSup.stateSpacePoints().printDataSummary(K_Shock_points, 'K_Shock_points')
#
#         simuSup.stateSpacePoints().printDataSummary(B_Mean_statespace_span, 'B_Mean_statespace_span')
#         simuSup.stateSpacePoints().printDataSummary(B_Shock_points, 'B_Shock_points')
#
#     '''
#     Return Sequenceis crucial, can not change,
#     '''
#
#     return [[K_ChoicePoints, K_Mean_statespace_span, K_Shock_points],
#             [B_ChoicePoints, B_Mean_statespace_span, B_Shock_points]]
