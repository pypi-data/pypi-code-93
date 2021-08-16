def add_visit(propfile,outname,visittemplate,visitnumber,targetname,line_index=None):
    ##### propfile = path to .prop file to be edited. This file will be open, but will not be changed; changes will be implemented and saved to a new file specified by outname.
    ##### outname = path to write the updated .prop file.
    ##### visittemplate = e.g., exposureconf_G280.json
    ##### visitnumber = two-digit string satisfied proposal requirements
    ##### targetname = string of target name corresponding to this visit, and to fixed target list.
    ##### line_index = line number to be added this visit info. If None, will add to the EOF.
    import json
    start_at_eof = False
    if not line_index:
        print('Finding EOF ...\n')
        f = open(propfile,'r')
        t0 = f.readlines()
        f.close()
        line_index = len(t0)
        print('This visit will be added at EOF: line {0}\n'.format(line_index))
        start_at_eof = True
    #####
    print('Grabbing the original file ...\n')
    f = open(propfile,'r')
    t0 = f.readlines()
    t1 = t0[:line_index]
    t3 = t0[line_index:]
    f.close()
    #####
    print('Grabbing visit template ...\n')
    f = open(visittemplate,'r')
    visitinfo = json.loads(f.readlines()[0])
    f.close()
    #####
    print('Creating {0} ...\n'.format(outname))
    f = open(outname,'w')
    f.writelines(t1)
    #####
    print('Writing visit info ...\n')
    for i in visitinfo:
        f.writelines('\n')
        for j in visitinfo[i]:
            if j=='Visit_Number':
                t = visitinfo[i][j] + visitnumber + '\n'
                f.writelines(t)
            elif j=='Target_Name':
                t = visitinfo[i][j] + targetname + '\n'
                f.writelines(t)
            else:
                t = visitinfo[i][j] + '\n'
                f.writelines(t)
    f.writelines(t3)
    f.close()   
    #####
    print('Finish ...\n')
