def update_visits_from_sheet(sheet_df,propfile,outname,verbal=True):
    """
    This function updates the propfile with a sheet_df (the Google sheet).
        Arguments:
            - sheet_df = pandas.DataFrame of the Google sheet. Use GoogleSheetReader to facilitate this.
            - propfile = path to .prop file
            - outname = path to .prop output file
            - verbal = bool. If True, this will show messages.
    """
    if verbal: print('Start update_visits_from_sheet ... \n')
    import os
    from rolling_snapshot_proposal_editor.update_status_SC import update_status_SC
    from rolling_snapshot_proposal_editor.update_status_RN import update_status_RN
    os.system('cp {0} {1}'.format(propfile,outname))
    if verbal: print('Grabbing info from sheet ... \n')
    targetnumberlist_new = sheet_df['Target Number'].values
    targetnamelist_new = sheet_df['Name'].values
    statuslist_new = sheet_df['Status'].values
    visitdigitlist_new = sheet_df['Visit Number First Digit'].values
    visitNlist_new = sheet_df['N'].values
    filterslist_new = sheet_df['Filters'].values
    for ii,targetnumber in enumerate(targetnumberlist_new):
        status = statuslist_new[ii]
        targetname = targetnamelist_new[ii].upper()
        visitdigit = visitdigitlist_new[ii]
        visitN = visitNlist_new[ii]
        filters = filterslist_new[ii]
        if status[0] in {'S','C'}: update_status_SC(outname,targetnumber,targetname,status,verbal)
        elif status[0] in {'R','N'}: update_status_RN(outname,targetnumber,targetname,status,visitdigit,visitN,filters,sheet_df,verbal)
    if verbal: print('Finish update_visits_from_sheet.\n')