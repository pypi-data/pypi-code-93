import random


def raffle(list):

    kay = []
    for li in list:
        random.shuffle(list)

        kay.append(list[0])
        list = list[1:]
    random.shuffle(list)
    return kay
