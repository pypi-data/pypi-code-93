import numpy as np


class Program:
    SIZE = 32

    def __init__(self, codes):
        if len(codes) != Program.SIZE:
            raise ValueError(
                f"Programs must be created with exactly {Program.SIZE} codes"
            )
        self._codes = list(codes)
        self.data = {}


    def __getitem__(self, ix):
        return self._codes[ix] 

    def __len__(self):
        return self.find_end(0)

    def arity_at(self, ix):
        return Program.arity_of(self._codes[ix])

    def find_end(self, ix):
        l = 1
        while True:
            if ix >= Program.SIZE:
                # Invalid program
                return 0

            a = self.arity_at(ix)
            l += a - 1
            ix += 1

            if l == 0:
                return ix

    def __hash__(self):
        # Convert the codes anctually in use to a tuple
        t = tuple([self.qid]+self._codes[0:len(self)])
        
        # Use buildin hash for tuples
        return hash(t)

    def __repr__(self):
        return "<P " + repr(self._codes) + ">"

    @staticmethod
    def arity_of(code:int):
        arity = code // 1000
        if arity>=10: 
            arity = 0
        return arity

    def from_arity_and_index(arity, index):
        if arity == 0:
            arity = 10
        return arity * 1000 + index

    def to_json(self):
        return {"codes": self._codes, "data": self.data, "qid": self.qid}
