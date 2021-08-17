def _find_lastline(template_dict,propfile):
    ##### Internally used
    keys = list(template_dict.keys())
    N = len(keys)
    #####
    target_lastline = None
    f = open(propfile,'r')
    t = f.readlines()
    for ii,i in enumerate(t):
        tt = i.split()
        try:
            if tt[0]=='{0}:'.format(keys[0]):
                target_lastline = ii+N # 1-indexing
        except:
            pass
    f.close()
    return target_lastline
