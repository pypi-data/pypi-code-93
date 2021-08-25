def unanimous(list, arg):
    for li in list:
        if arg == li:
            continue
        else:
            return False
    return True
