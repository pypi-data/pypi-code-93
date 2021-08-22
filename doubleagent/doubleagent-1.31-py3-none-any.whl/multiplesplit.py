import doubleagent


def multiplesplit(string, inja_list):
    string = string.split(inja_list[0])
    inja_list = inja_list[1:]
    if isinstance(inja_list, list) == True:
        for la in inja_list:
            string_list = []
            for li in string:
                li = li.split(la)
                string_list.append(li)
            string = doubleagent.ll2l(string_list)

    if isinstance(inja_list, list) == False:
        string_list = []
        for li in string:
            li = li.split(inja_list)
            string_list.append(li)
        string = doubleagent.ll2l(string_list)
    if len(string) == 1:
        string = string[0]
    return string
