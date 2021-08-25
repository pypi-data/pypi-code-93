def add_fixed_target(propfile,targetinfo,outname,line_index=None):
    ##### propfile = path to .prop file to be edited. This file will be open, but will not be changed; changes will be implemented and saved to a new file specified by outname.
    ##### targetinfo = a template dict of what information to be written.
    ########## for updating fixed targets, use fixed_target.json for the dict template.
    ##### outname = path to write the updated .prop file.
    ##### line_index = 1-indexing of the previous fixed target's last line (i.e., Comments: ...). If None, the code will automatically search for the last line.
    from rolling_snapshot_proposal_editor._find_lastline import _find_lastline
    if not line_index:
        print('Finding line_index ...\n')
        line_index = _find_lastline(targetinfo,propfile)
        print(line_index)
    #####
    print('Grabbing the original file ...\n')
    f = open(propfile,'r')
    t0 = f.readlines()
    t1 = t0[:line_index]
    t3 = t0[line_index:]
    f.close()
    #####
    print('Creating {0} ...\n'.format(outname))
    f = open(outname,'w')
    f.writelines(t1)
    f.writelines('\n')
    for i in targetinfo:
        t = targetinfo[i] + '\n'
        f.writelines(t)
    f.writelines(t3)
    f.close()   
    #####
    print('Finish ...\n')
