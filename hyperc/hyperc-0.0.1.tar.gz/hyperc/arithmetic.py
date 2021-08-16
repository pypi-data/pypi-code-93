import itertools
import hashlib, pickle
import hyperc.util

SUMS = []
MULS = []
DIVS = []
GTS = []
GES = []
SUMS_HASH = set()
MULS_HASH = set()
DIVS_HASH = set()
GTS_HASH = set()
GES_HASH = set()

class SumResult:
    term1: int
    term2: int
    summ: int

    @hyperc.util.side_effect_decorator
    def __str__(self):
        return f'{self.term1}+{self.term2}={self.summ}'

    def self_hash(self):
        h = hashlib.md5()
        h.update(pickle.dumps(self.term1, self.term2, self.summ))
        return h.digest()

class MulResult:
    term1: int
    term2: int
    mul: int

    def self_hash(self):
        h = hashlib.md5()
        h.update(pickle.dumps(self.term1, self.term2, self.mul))
        return h.digest()

class DivResult:
    term1: int
    term2: int
    div: int
    
    # def __str__(self):
    #     return f'{self.term1}+{self.term2}={self.div}'

    def self_hash(self):
        h = hashlib.md5()
        h.update(pickle.dumps(self.term1, self.term2, self.div))
        return h.digest()

class GreaterThan:
    less_val: int
    greater_val: int

    def self_hash(self):
        h = hashlib.md5()
        h.update(pickle.dumps(self.less_val, self.greater_val))
        return h.digest()

class GreaterEqualThan:
    less_val: int
    greater_val: int

    def self_hash(self):
        h = hashlib.md5()
        h.update(pickle.dumps(self.less_val, self.greater_val))
        return h.digest()

class SimpleIntegerFactory:
    def __init__(self, num_list):
        self.numbers=num_list
        self.generate_operations()
        self.generate_gt_ge()
        self.heap = [SUMS, MULS, DIVS, GTS, GES]  # Don't forget to add all heap objects here
    
    def heap_len(self):
        return sum([len(v) for v in self.heap])

    def get_objects(self):
        return list(self.numbers.values()) + \
                self.sums + self.muls + self.divs + self.gts + self.ges

    def generate_operations(self):
        global SUMS
        global MULS
        global DIVS
        global SUMS_HASH
        global MULS_HASH
        global DIVS_HASH
        self.sums=SUMS
        self.muls = MULS
        self.divs = DIVS
        for a, b in itertools.product(self.numbers, repeat=2):
            s = SumResult()
            m = MulResult()

            s.term1 = m.term1 = a
            s.term2 = m.term2 = b
            sumn = a + b
            muln = a * b
            if sumn in self.numbers:
                s.summ = sumn
                h = (s.term1, s.term2, s.summ)
                if not h in SUMS_HASH:
                    self.sums.append(s)
                    SUMS_HASH.add(h)
            if muln in self.numbers:
                m.mul = muln
                h = (m.term1, m.term2, m.mul)
                if not h in MULS_HASH:
                    self.muls.append(m)
                    MULS_HASH.add(h)
            if b != 0:
                d = DivResult()
                d.term1 = a
                d.term2 = b
                divn = a // b
                if divn in self.numbers:
                    d.div = divn
                    h = (d.term1, d.term2, d.div)
                    if not h in DIVS_HASH:
                        self.divs.append(d)
                        DIVS_HASH.add(d)

    def generate_gt_ge(self):
        global GES
        global GES_HASH
        global GTS
        global GTS_HASH

        self.gts = GTS
        self.ges = GES
        for a, b in itertools.product(self.numbers, repeat=2):
            if a > b:
                gt = GreaterThan()
                gt.less_val = b
                gt.greater_val = a
                h = (gt.less_val, gt.greater_val)
                if not h in GTS_HASH:
                    GTS_HASH.add(h)
                    self.gts.append(gt)
            if a >= b:
                ge = GreaterEqualThan()
                ge.greater_val = a
                ge.less_val = b
                h = (ge.less_val, ge.greater_val)
                if not h in GES_HASH:
                    GES_HASH.add(h)
                    self.ges.append(ge)

