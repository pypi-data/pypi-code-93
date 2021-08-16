from hyperc.poc_symex import solve


class CA:
    pass


class CB:
    pa: CA


def myact(ob: CB):
    ob.pa = oa1
    return None


def myact2():
    ob.pa = CA()
    return CA()


oa = CA()
oa1 = CA()

ob = CB()
ob.pa = oa

def goal(ob: CB):
    assert ob.pa == oa1


def _run():
    print(solve(goal))


if __name__ == '__main__':
    _run()
