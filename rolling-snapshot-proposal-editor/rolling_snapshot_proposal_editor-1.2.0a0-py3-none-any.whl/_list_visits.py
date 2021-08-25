def _list_visits(propfile):
    ##### internally used
    dictvisits = {}
    print('Reading {0} ...\n'.format(propfile))
    f = open(propfile,'r')
    t0 = f.readlines()
    f.close()
    #####
    print('Listing visits ...\n')
    for ii,i in enumerate(t0):
        try:
            if i.split()[0]=='Visit_Number:':
                dictvisits[i.split()[-1]] = ii # 0-indexing
        except:
            pass
    #####
    print('Finish ...\n')
    return dictvisits
