import inspect
import itertools
import sys
import copy

import hyperc.poc_symex
from base64 import b64encode
from collections import defaultdict
from hashlib import sha1
from itertools import chain, tee
from pprint import pprint

import logging

import re
def stripComments(code):
    code = str(code).strip()
    m = re.match(r'^([^#]*)#(.*)$', code)
    if m:
        return m.group(1)
    return code

log = logging.getLogger(__name__)


class MCDCPlacesProxiesMap:
    places2proxies_map: dict  # of str-str
    proxies2places_map: dict  # of str-str
    ids_map: dict
    def __init__(self, places2proxies_map, proxies2places_map, ids_map) -> None:
        self.places2proxies_map = places2proxies_map
        self.proxies2places_map = proxies2places_map
        self.ids_map = ids_map

class McdcVals:
    def __init__(self):
        self.new_eqs = list()  # New ones
        self.eqs_vals = dict()  # Current values 'eq-key': True or False
        self.eqs_on_line = defaultdict(list)  # Number of eq per line
        self.code_cache = dict()
        
        # These are for RWB-MCDC issue#342
        self.places2proxies_map = {}  # Places to ids, str-str
        self.proxies2places_map = {}  # IDs to places, str-str
        self.ids_map = {}  # IDs(str) to real proxies
        self.current_replacements = {}  # places to places
        self.linekey_counter = defaultdict(lambda: 0)
    
    def register_map(self, place_id: str, hcp: "HCProxy"):
        self.places2proxies_map[place_id] = hcp._self_id()
        self.proxies2places_map[hcp._self_id()] = place_id
        self.ids_map[hcp._self_id()] = hcp 

    def check_and_replace(self, hcp):
        # print("RWB>>> CHECK IF CAN REPLACE", hcp._self_id(), self.current_replacements)
        if hcp._self_place_id_linked() in self.current_replacements:
            replace_with_place = self.current_replacements[hcp._self_place_id_linked()]
            if not replace_with_place in self.places2proxies_map:
                raise hyperc.poc_symex.HCAssertionException()  # branch does not exist
                                                               # if asked to equal non-existing
            object_id_at_place = self.places2proxies_map[replace_with_place]
            assert type(self.ids_map[object_id_at_place]) != str, f"{self.ids_map}"
            # print("RWB>> returning DIFFERENT FOR", hcp._self_id(), hcp._self_place_id_linked())
            return self.ids_map[object_id_at_place].shadowed
        return hcp

    def get_chached_frameinfo(self, frame):
        key = f'{frame.f_code.co_filename}:{frame.f_lineno}'
        if key not in self.code_cache:
            filename, line_number, function_name, lines, index = inspect.getframeinfo(frame)
            if not lines: lines = [""]  # pyodide
            self.code_cache[key] = (filename, line_number, lines[0])
        return self.code_cache[key]

    def before(self):
        self.new_eqs = []
        self.eqs_on_line = defaultdict(list)  # Number of eq per line
        self.places2proxies_map = {}
        self.proxies2places_map = {}
        self.ids_map = {}
        self.linekey_counter = defaultdict(lambda: 0)

    def after(self, mcdc_it):
        self.eqs_on_line = defaultdict(list)
        self.eqs_vals = mcdc_it.send(self.new_eqs)
    
    def export_places_maps(self):
        return MCDCPlacesProxiesMap(
            places2proxies_map=copy.copy(self.places2proxies_map),
            proxies2places_map=copy.copy(self.proxies2places_map),
            ids_map=copy.copy(self.ids_map)
        )

    def get_place_id(self, name=""):
        found = False
        line_number = -1
        all_code = ""
        for frame in yield_back(sys._getframe(1)):
            filename, line_number, code = self.get_chached_frameinfo(frame)
            all_code = f"{line_number}:{code}"
            if "poc_symex.py" not in filename and "_self_" not in code and not "mcdc" in code and not "HCProxy" in code:
                # print("RWB2>>> CODE", code, filename)
                found = True
                break
        assert found
        line_key = f'{line_number}-{all_code}'
        self.linekey_counter[line_key] += 1
        key = f'{name}->{self.linekey_counter[line_key]}:{line_key}'  # Unique key, I hope
        return key


def safe_id(v):
    if isinstance(v, hyperc.poc_symex.HCProxy):
        return v._self_id()
    return id(v)


def yield_back(frame):
    while frame.f_back:
        yield frame.f_back
        frame = frame.f_back

def check_and_expand(self, other, mcdc_vals: McdcVals, locators: tuple):
    new_eqs = mcdc_vals.new_eqs
    eqs_vals = mcdc_vals.eqs_vals
    eqs_on_line = mcdc_vals.eqs_on_line
    line_number = None
    found = False
    # for fi in getouterframes_fast(frame):
    for frame in yield_back(sys._getframe(1)):
        filename, line_number, code = mcdc_vals.get_chached_frameinfo(frame)
        # print(code)
        # grep -n HCAssert hyperc/poc_symex.py | cut -d":" -f1 | xargs | sed s/\ /,/g
        # WARNING!! This is dangerous and unsafe check: if the lines in poc_symex are OFF
        # this "lineno optimization" will throw weird errors and tests failing!
        if "HCAssertionException" in code:  # or line_number in [796,818,819,820,831,832,833,844,845,846,857,858,859,914,922,1044,1257,1278,1322,1405,1413,1423]:
            return True
        if code.strip().startswith("assert"): 
            scode = stripComments(code)
            # print(code)
            if (not "(" in scode and not ")" in scode and not "\\" in scode and len(scode.split("==")) == 2 and 
               len(scode.split()) == 4):
            #    print("Skipping assert", scode)
               return True
            elif (not "(" in scode and not ")" in scode and not "\\" in scode and len(scode.split("!=")) == 2 and 
               len(scode.split()) == 4):
               return False
        if any(locator in code for locator in locators) and 'mcdc' not in code:
            found = True
            break
    if not found:
        return True
    # hs = b64encode(sha1(code.encode('utf8')).digest()).decode('ascii')  # FIXME more reliable way
    hs = code
    line_key = f'{line_number}-{hs} {locators}'
    eqs_on_line[line_key].append(None)  # may be anything used just for counting
    mynumber = len(eqs_on_line[line_key])  # my occurrence in the line
    # key = f'{mynumber}:{line_key} {self}=={other}'  # Unique key, I hope
    key = f'{mynumber}:{line_key}'  # Unique key, I hope
    if key not in eqs_vals:  # if not in eq:T/F dict this is the new one
        # print(f"New branch discovered! {key} \n\t {code}")
        new_eqs.append(key)
    del frame  # No memory leakage
    return eqs_vals.get(key, True)  # always return True if first time seen


def gen_combinations(it, length):
    vals = list(itertools.product((True, False), repeat=length))  # [False, True, False, False, True]
    for comb in itertools.product(it,
                                  vals):  # We "add" a "column" of [False, True]... to  partially exhausted generator
        yield list(chain.from_iterable(comb))  # Flatten one level of nesting


def gen_mcdc(seen):
    newdata = list()
    it = itertools.product((True, False), repeat=len(seen))
    next(it)  # We are not interested in True True True ...
    visited_branches = set()
    while True:
        assert not set(seen) & set(newdata)  # New __eq__ keys must always be new
        seen.extend(newdata)
        it = gen_combinations(it, len(newdata))
        newdata = list()
        for combination in it:
            full_test_comb = tuple(zip(seen, combination))
            if full_test_comb in visited_branches: 
                continue
            visited_branches.add(full_test_comb)
            line_groups = defaultdict(set)  # Grouped by line number
            absurd = False
            for rec in full_test_comb:
                ln = rec[0].split("-")[1].strip()
                if not ln.startswith("if") or "or" in ln or not ln.split("\n")[0].strip().endswith(":"):
                    # FIXME: multiline IFs are not supported!
                    continue  # Only if-AND combinations are eligible
                lineno = rec[0].split(":")[1].split("-")[0]
                line_groups[lineno].add(rec[1])
                if len(line_groups[lineno]) > 1:
                    absurd = True
                    break
            if absurd:
                continue
            item = dict(full_test_comb)
            # possible_combinations = 2 ** len(combination)
            # number = sum(int(bit) << position
            #              for (position, bit) in
            #              enumerate(reversed(combination)))
            # print(f'{possible_combinations} / {number}'.center(80, '='))
            # pprint(item)
            newdata = (yield item)  # Receiving new __eq__ keys
            if newdata:
                it = chain((combination,), it)  # we are still instereted in current combination
                break  # We need to update child generator
        if not newdata:
            break  # Only way to reach this point is to exahaust iterator
