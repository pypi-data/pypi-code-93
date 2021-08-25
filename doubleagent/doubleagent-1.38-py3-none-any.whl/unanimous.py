def unanimous(list):
    for li in list:
        if list[0] == li:
            continue
        else:
            return False
    return True
