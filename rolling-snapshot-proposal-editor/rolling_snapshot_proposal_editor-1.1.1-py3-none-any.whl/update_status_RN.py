def update_status_RN(propfile,targetnumber,targetname,status,visitdigit,visitN,filters,sheet_df,verbal=True):
    """
    This function updates visits in the propfile given (targetnumber,targetname) with status R or N.
    For R (repeat) status, the target is already existed in the propfile, but we would like to change the total number of its visits (visitN) by keeping the visit number's first digit (visitdigit) and filter info (filters) the same.
        Arguments:
            - propfile = path to .prop file
            - targetnumber = str
            - targetname = str
            - status = str. It is in {'R','N'}
            - visitdigit = str, 36-base one digit (i.e., 0...Z)
            - visitN = int or str
            - filters = str. It must be a correct keyword to search for a template library (e.g., 'visits_G280'). Use TemplateHandler to facilitate this.
            - sheet_df = pandas.DataFrame of the observing sheet (i.e., Google sheet)
            - verbal = bool
    """
    if verbal: print('Start update_status_RN({0},{1},{2},{3},{4},{5},{6},{7},{8}) ...\n'.format(propfile,targetnumber,targetname,status,visitdigit,visitN,filters,'sheet_df',verbal))
    from rolling_snapshot_proposal_editor.find_targetname_in_visits import find_targetname_in_visits
    from rolling_snapshot_proposal_editor.remove_visit import remove_visit
    from rolling_snapshot_proposal_editor.templatehandler import TemplateHandler
    from rolling_snapshot_proposal_editor.add_visit import add_visit
    from rolling_snapshot_proposal_editor.get_available_visitnumber import get_available_visitnumber
    import numpy as np
    lineindex_visitnumber_targetname_list = find_targetname_in_visits(propfile)
    vn_list = []
    for i in lineindex_visitnumber_targetname_list:
        index,vn,tn = i
        if targetname==tn: vn_list.append(vn)
    if verbal: print('Target {0} {1} had {2} visits in the old proposal. It will be updated to {3} visits.\n'.format(targetnumber,targetname,len(vn_list),visitN))
    niter = np.abs(len(vn_list) - int(visitN))
    if len(vn_list) > int(visitN):
        if verbal: print('Remove {0} visits from the old proposal.\n'.format(niter))
        for i in np.arange(niter): remove_visit(propfile,propfile,vn_list[-1-i])
    elif len(vn_list) < int(visitN):
        if verbal: print('Add {0} visits from the old proposal.\n'.format(niter))
        visitnumber_available = get_available_visitnumber(propfile,visitdigit,verbal)
        for i in np.arange(niter): 
            visittemplate = TemplateHandler().templatedict[filters]
            visitnumber = visitnumber_available[i]
            add_visit(propfile=propfile,outname=propfile,visittemplate=visittemplate,visitnumber=visitnumber,targetname=targetname,line_index=None)
            print('Visit {0} added ... \n'.format(visitnumber))
    if verbal: print('Finish update_status_RN.\n')
