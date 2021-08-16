from hyperc.api import schedule


class CA:
    pass


class CB(CA):
    pa: CA


def myact(ob: CB):
    ob.pa = oa1


def myact2():
    ob.pa = CA()
    return CA()


oa = CA()
oa1 = CA()

ob = CB()
ob.pa = oa


def _run():
    return schedule(lambda ob: ob.pa == oa1)


if __name__ == '__main__':
    _run()
