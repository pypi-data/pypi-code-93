
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

class CS:
    s: set
    def __init__(self):
        self.s = set()

def add_oa_to_cs(aas: CS, oa: CA):
    aas.s.add(oa)

def remove_oa_to_cs(aas: CS, oa: CA):
    aas.s.remove(oa)

def if_in_then_iadd(aas: CS, oz: CZ):
    if oz in aas.s:
        oz.i += 1  # FIXME: this produces wrong negation for setattr (absurd one)

def if_remove_oa_to_cs(aas: CS, oa: CA):
    if oa in aas.s:
        aas.s.remove(oa)
    else:
        oa.cz = CZ()
    
def complex_if(oa: CA, oa2: CA):
    if oa.pa != oa2.pa:
        oa.pa = oa1
    else:
        oa2.pa = oa1

glo_s = set()

def assign_to_global_set(os: CS):
    global glo_s
    glo_s = os.s

def add_to_global_set(oa: CA):
    glo_s.add(oa)

def assign_global_set_to_obj(os: CS):
    os.s = glo_s

new_s = set()

some_other_s = set([CZ(), CZ()])

def create_new_set():
    global new_s
    new_s = set()

class T:
    f: CZ
    def foo(self: "T", data: CZ):
        self.f = data

def run_method(ot: T, oz: CZ):
    ot.foo(oz)

def assign_new_set_with_elements(os: CS):  # FIXME: for this case, need special translation when assigning
    os.s = set((CZ(), CZ()))

def create_new_global_set_with_elements():  # FIXME: special path for globals
    global new_s
    new_s = set((CZ(), CZ()))

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
