def prop_profiling(propfile,json_template,by_keyword=False,keyword='None'):
    ##### propfile = .prop file
    ##### json_template = e.g., fixed_target.json, visits.json, exposure.json
    ##### by_keyword = bool. Set True, if you want to search by using a keyword instead of using json_template.
    ##### keyword = str e.g., 'Target_Number:'. Note that most keywords in propfile will have a comma ':' at the end.
    ##### This function returns line index (0-indexing) and content of the line in propfile given the first keyword presented in json_template, or given keyword (if by_keyword = True).
    import json
    #####
    print('Read propfile ...\n')
    f = open(propfile,'r')
    t0 = f.readlines()
    f.close()
    #####
    if not by_keyword:
        print('Read json_template ...\n')
        f = open(json_template,'r')
        tj = json.loads(f.readlines()[0])
        f.close()
        keyword = tj[list(tj.keys())[0]].split()[0]
    else:
        keyword = keyword
    print("""Search keyword: '{0}'\n""".format(keyword))
    #####
    output = []
    for ii,i in enumerate(t0):
        if keyword in i.split():
            output.append((ii,i))
    #####
    print('Return profile ...\n')
    return output