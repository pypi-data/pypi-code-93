from hyperc.poc_symex import solve

class CZ:
    i: int
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


def myact(ob: CB):
    ob.pa = oa1
    c = ob.pa
    ob.pa = oa 
    if c == oa1:
        pass

#
def myact1(oa: CA, ob: CB):
    ob1.pa = ob.pa = oa


def myact2():
    ob.pa = CA(CZ()) # pa has prev value
    oa.pa = CA(CZ()) # testing no prev value
    return CA(CZ())


def myact3():
    ob.pa = oc.pb.pa
    myact(ob1)
    return CA(CZ())

#
# def myact4(ob: CB):
#     print(ob.pa)
#     assert ob == ob1
#     print(type(ob1))
#     print(ob1._self_id())

def myact5():
    ob.pa = oc.pb.pa
    # if ob.pa == oc.pb.pa:  # Doesn't work because of above
        # pass
    myact(ob1)
    return CA(CZ())

def myact6(ob: CB):
    ob.pa == oa1 # this is translated only to one dereferencing (the attr must exist)
    # (CB-pa ?ob1 ?v1)
    # (module-oa1 ?oa1 ?v1)

def myact7(ob: CB, ob2: CB):
    if ob.pa != ob2.pa:
        pass

def badact():
    oa.pa = oa1 # Will only set in EFFECT of this action 
                # unless a sufficient split exists
    if oa.pa == oa1: # WON'T HAPPEN! without a split
        oa1.pa = oa1
        complete = True # This has no effect as it is a local unused variable
    else:
        ob.pa = oa1
        complete = False

def intact():
    global z
    z = CZ() 
    z.i += 1  # TODO: check if setattr is cancelled
              # by adding setattr in CZ init and looking at pddl
              # TODO: we know that z.i does not exist, so this should not compile at all...


z = CZ()  # TODO: delete this and re-try ineqact to check if it will generate global
def ineqact(a: int, b: int):
    global z
    if a > b:
        z = CZ()
    # else:
    #     myact3()

def ineqact_newglo(a: int, b: int):
    global znew
    if a > b:
        znew = CZ()
    # else:
    #     myact3()


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
