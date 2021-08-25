

def overlapchecker(list):
    overlap = False

    for a in list:
        list = list[1:]

        if a in list:
            overlap = True
            break
    return overlap
