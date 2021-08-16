import inspect
import itertools
from base64 import b64encode
from collections import defaultdict
from hashlib import sha1
from itertools import chain, tee

new_eqs = list()  # New ones
eqs_vals = dict()  # Current values 'eq-key': True or False
eqs_on_line = defaultdict(list)  # Number of eq per line


class Proxy:
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.name

    def __eq__(self, other):
        for frameinfo in inspect.stack():
            if '==' in frameinfo.code_context[0]:  # FIXME more reasonable caller detection
                frame, filename, line_number, function_name, lines, index = frameinfo
                break
        hs = b64encode(sha1(frameinfo.code_context[0].encode('utf8')).digest()).decode(
            'ascii')  # FIXME more reliable way
        line_key = f'{line_number}-{hs}'
        eqs_on_line[line_key].append(None)  # may be anything used just for counting
        mynumber = len(eqs_on_line[line_key])  # my occurrence in the line
        key = f'{mynumber}:{line_key} {self}=={other}'  # Unique key, I hope
        if key not in eqs_vals:  # if not in eq:T/F dict this is the new one
            new_eqs.append(key)
        del frame  # No memory leakage
        return eqs_vals.get(key, True)  # always return True if first time seen


def gen_combinations(it, length):
    vals = itertools.product((True, False), repeat=length)  # [False, True, False, False, True]
    for comb in itertools.product(it,
                                  vals):  # We "add" a "column" of [False, True]... to  partially exhausted generator
        yield list(chain.from_iterable(comb))  # Flatten one level of nesting


def gen_mcdc(seen):
    newdata = list()
    it = itertools.product((True, False), repeat=len(seen))
    next(it)  # We are not interested in True True True ...
    while True:
        assert not set(seen) & set(newdata)  # New __eq__ keys must always be new
        seen.extend(newdata)
        it = gen_combinations(it, len(newdata))
        newdata = list()
        for combination in it:
            item = dict(zip(seen, combination))
            newdata = (yield item)  # Receiving new __eq__ keys
            if newdata:
                it = chain([combination], it) # we are still instereted in current combination
                break  # We need to update child generator
        if not newdata:
            break  # Only way to reach this point is to exahaust iterator


if __name__ == '__main__':
    new_eqs = list()
    eqs_vals = dict()
    eqs_on_line = defaultdict(list)

    p1 = Proxy('p1')
    p2 = Proxy('p2')
    p3 = Proxy('p3')
    p4 = Proxy('p4')
    p5 = Proxy('p5')
    p6 = Proxy('p6')


    def myfunc():
        if p1 == p2 and p5 == p6:
            print('branch 1')
            if p3 == p2:
                print('branch 1.1')
                if p3 == p4:
                    print('branch 1.1.1')
                    pass
            else:
                print('branch 1.2')
                if p4 == p2:
                    print('branch 1.2.1')
                    pass
            if p1 == p3:
                print('branch 1.3')
                pass
        else:
            print('branch 2')
            if p5 == p1:
                print('branch 2.1')
                pass
        print('=' * 5)


    myfunc()
    it = gen_mcdc(new_eqs)
    comb = next(it)  # True True True
    print(new_eqs)
    while it:
        new_eqs = list()
        print(comb)
        myfunc()
        eqs_on_line = defaultdict(list)
        comb = it.send(new_eqs)
        eqs_vals = comb
