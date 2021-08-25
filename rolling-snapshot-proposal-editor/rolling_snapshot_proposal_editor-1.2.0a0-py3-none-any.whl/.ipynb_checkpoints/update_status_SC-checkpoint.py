def update_status_SC(propfile,targetnumber,targetname,status,verbal=True):
    """
    This function updates visits in propfile for a (targetnumber,targetname) that has S_XX or C_XX (for scheduled/completed with visit number XX). In this routine, we assume that in the updated proposal the target will have only visit XX left.
        Arguments:
            - propfile = path to .prop file
            - targetnumber = str
            - targetname = str
            - status = str. It is in {S_XX,C_XX} for XX = visit number where X = 36-base digit (i.e., from 0...Z)
            - verbal = bool
    """
    if verbal: print('Start update_status_SC({0},{1},{2},{3}) ...\n'.format(propfile,targetnumber,targetname,status))
    from rolling_snapshot_proposal_editor.find_targetname_in_visits import find_targetname_in_visits
    from rolling_snapshot_proposal_editor.remove_visit import remove_visit
    lineindex_visitnumber_targetname_list = find_targetname_in_visits(propfile)
    for i in lineindex_visitnumber_targetname_list:
        index,vn,tn = i
        if targetname==tn and status.split('_')[1]!=vn: remove_visit(propfile,propfile,vn) 
    if verbal: print('Finish update_status_SC.\n')
