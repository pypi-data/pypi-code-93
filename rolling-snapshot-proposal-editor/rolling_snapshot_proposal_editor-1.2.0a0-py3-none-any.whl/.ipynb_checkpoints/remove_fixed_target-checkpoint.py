def remove_fixed_target(propfile,target_number,json_template,outname,do_remove_visits=True):
    ##### propfile = path to .prop file to be edited. This file will be open, but will not be changed; changes will be implemented and saved to a new file specified by outname.
    ##### target_number = string of 'Target_Number:' to be removed.
    ########## This assumes 'Target_Number:' starting each fixed target section.
    ##### json_template = e.g., fixed_target.json to read the string format, to count for the number lines to be removed.
    ##### outname = path to write the updated .prop file.
    ##### do_remove_visits = bool. If True, all visits associating with the target will be removed.
    import json
    from rolling_snapshot_proposal_editor.find_targetname_in_targetlist import find_targetname_in_targetlist
    from rolling_snapshot_proposal_editor.find_targetname_in_visits import find_targetname_in_visits
    from rolling_snapshot_proposal_editor.remove_visit import remove_visit
    print('load json_template ...\n')
    f = open(json_template,'r')
    template_dict = json.loads(f.readlines()[0])
    f.close()
    keys = list(template_dict.keys())
    N = len(keys)
    #####
    print('read propfile ...\n')
    f = open(propfile,'r')
    propread = f.readlines()
    f.close()
    #####
    print('read target name ... \n')
    target_name_list = find_targetname_in_targetlist(propfile)
    for ii,i in enumerate(target_name_list):
        if target_name_list[ii][1] == target_number:
            target_name = target_name_list[ii][2]
            break
    #####
    print('find line number ...\n')
    linenum = None
    for ii,i in enumerate(propread):
        tt = i.split()
        try:
            if tt[0]=='{0}:'.format(keys[0]):
                if tt[1]==target_number: # 1-indexing
                    linenum = ii
                    break
        except:
            pass
    print(linenum)
    #####
    print('remove ...\n')
    t1 = propread[:linenum-1]
    t2 = propread[linenum+N:]
    #####
    print('Creating {0} ...\n'.format(outname))
    f = open(outname,'w')
    f.writelines(t1)
    f.writelines(t2)
    f.close()   
        #####
    if do_remove_visits:
        print('Removing visits associating with target number {0}, target name {1} ...\n'.format(target_number,target_name))
        visit_targetname_list = find_targetname_in_visits(outname)
        for ii,i in enumerate(visit_targetname_list):
            _,visitnumber,visittargetname = visit_targetname_list[ii]
            if visittargetname == target_name:
                remove_visit(outname,outname,visitnumber)
    #####
    print('Finish ...\n')
