def list_visits(propread,verbal=True):
    dictvisits = {}
    if verbal: print('Listing visits ...\n')
    for ii,i in enumerate(propread):
        try:
            if i.split()[0]=='Visit_Number:':
                print('here')
                dictvisits[i.split()[-1]] = ii # 0-indexing
        except:
            pass
    #####
    if verbal: print('Finish ...\n')
    print(dictvisits)
    return dictvisits
