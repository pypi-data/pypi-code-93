def get_available_visitnumber(propfile,visitdigit,verbal=True):
    """
    This function lists visit numbers which are available to be used given propfile and visitdigit (i.e., the first digit of the visit number).
    Visit number has two digits (e.g., XX), each digit is 36-base (i.e., 0...Z).
        Arguments:
            - propfile = path to .prop file
            - visitdigit = 1-digit str with 36-base (i.e., 0...Z). Only uppercase for a character.
            - verbal = bool
        Returns:
            - a list of available visit numbers
    """
    print('Start get_availabel_visitnumber({0},{1},{2}) ... \n'.format(propfile,visitdigit,verbal))
    from rolling_snapshot_proposal_editor.find_targetname_in_visits import find_targetname_in_visits
    lineindex_visitnumber_targetname_list = find_targetname_in_visits(propfile)
    vn_list = []
    for i in lineindex_visitnumber_targetname_list:
        index,vn,tn = i
        if vn[0]==visitdigit: vn_list.append(vn)
    visit_seconddigit_all = ['0','1','2','3','4','5','6','7','8','9','A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
    vn_list_available = []
    for i in visit_seconddigit_all:
        t = visitdigit + i
        if t not in vn_list: vn_list_available.append(t)
    print('Return get_availabel_visitnumber.\n')
    return vn_list_available
