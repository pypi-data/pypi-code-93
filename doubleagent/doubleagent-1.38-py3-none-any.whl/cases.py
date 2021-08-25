import itertools


def cases(arr, num):
    a = []
    t = list(itertools.permutations(arr, num))
    for li in t:
        a.append(list(li))
    return a
