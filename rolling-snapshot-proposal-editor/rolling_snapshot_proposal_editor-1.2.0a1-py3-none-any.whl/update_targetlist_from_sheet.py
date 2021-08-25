def update_targetlist_from_sheet(sheet_df,propfile,outname,remove_visits=True,verbal=True):
    """
    This function compares active target list in sheet_df with the old list in propfile. 
    It removes all targets that are presented in the old prop file but not in the active list.
    New targets with status 'N' in sheet_df['Status'] will be added.
    It will also remove all associated visits with each removed targets, if remove_visits = True.
        Arguments:
            sheet_df = Google sheet in dataframe. Use GoogleSheetReader class to facilitate this.
            propfile = path to .prop file to be editted
            outname = path to the output .prop file
            remove_visits = bool. If True, all visits associated to
    """
    import os
    from rolling_snapshot_proposal_editor.prop_profiling import prop_profiling
    from rolling_snapshot_proposal_editor.templatehandler import TemplateHandler
    from rolling_snapshot_proposal_editor.remove_fixed_target import remove_fixed_target
    from rolling_snapshot_proposal_editor.prepare_targetinfo import prepare_targetinfo
    from rolling_snapshot_proposal_editor.add_fixed_target import add_fixed_target
    if verbal: print('Start update_targetlist_from_sheet ... \n')
    os.system('cp {0} {1}'.format(propfile,outname))
    if verbal: print('Grabbing active target list ...\n')
    activelist = sheet_df['Target Number'].values.astype(str)
    if verbal: print('Grabing old target list ...\n')
    oldlist = prop_profiling(outname,json_template=None,by_keyword=True,keyword='Target_Number:')
    if verbal: print('Comparing lists ...\n')
    oldlist_targetnumber = []
    #####
    removelist = []
    for i in oldlist:
        t = i[1].split()[-1]
        oldlist_targetnumber.append(t)
        tt = True if t not in activelist else False
        removelist.append(tt)
    if verbal: print('Removing target numbers {0} ... \n'.format(removelist))
    json_template = TemplateHandler().templatedict['fixed_target']
    for ii,i in enumerate(removelist):
        if i: remove_fixed_target(outname,oldlist_targetnumber[ii],json_template,outname,True)
    #####
    statuslist = sheet_df['Status'].values
    targetnumberlist = sheet_df['Target Number'].values
    for ii,status in enumerate(statuslist):
        if status=='N':
            targetnumber = targetnumberlist[ii]
            targetinfo = prepare_targetinfo(spreadsheet=sheet_df,read_spreadsheet_csv=False,targetnumber=targetnumber,json_template=TemplateHandler().templatedict['fixed_target'])
            add_fixed_target(propfile=outname,targetinfo=targetinfo,outname=outname,line_index=None)
            print('Added target number {0} ... \n'.format(targetnumber))
    if verbal: print('Finish update_targetlist_from_sheet.\n')    
        