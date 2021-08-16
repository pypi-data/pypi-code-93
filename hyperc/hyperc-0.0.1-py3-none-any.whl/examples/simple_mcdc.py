from hyperc.poc_symex import solve

class CZ:
    pass

class CA:
    cz: CZ
    pa: "CA" # ?? Py3.8 should do all types delayed??? # TODO: remove this line and create test
    def __init__(self, cz: CZ):
        self.cz = cz
    pass


class CB:
    pa: CA


class CC:
    pb: CB


def myact6(ob: CB):
    ob.pa == oa1 # this is translated only to one dereferencing (the attr must exist)
    # (CB-pa ?ob1 ?v1)
    # (module-oa1 ?oa1 ?v1)



oa = CA(CZ())
oa1 = CA(CZ())

ob = CB()
ob.pa = oa

ob1 = CB()

oc = CC()
oc.pb = CB()
oc.pb.pa = CA(CZ())

def goal(ob: CB):
    assert ob.pa == oa1

def _run():
    return solve(goal)


if __name__ == '__main__':
    _run()
