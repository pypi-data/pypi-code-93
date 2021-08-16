from collections import defaultdict
from hyperc.util import hcp_append_if_not
import itertools
from typing import final
import hyperc.poc_symex as hc
import hyperc.world
import logging
log = logging.getLogger("hyperc")
progress = logging.getLogger("hyperc_progress")


HCPCACHE = {}


def l1_flatten(t):
    """
    Flatten list of lists to one level
    """
    return [item for sublist in t for item in sublist]


def eliminate(l, stmt, v):
    """
    Eliminate variable from a statement (stmt) of the form (<bool>, (?v1, ?v2))
    given the list of statements l where (True (v2, v3)) means v1 and v2 equal
    returns a set of all possible eliminations
    """
    possible = set()
    v_idx = stmt[1].index(v)
    for stmt2 in l:
        if stmt == stmt2: continue
        if stmt2[0] and v == stmt2[1][0]:
            if v_idx == 0:
                possible.add((stmt[0], (stmt2[1][1], stmt[1][1])))
            else:
                possible.add((stmt[0], (stmt[1][0], stmt2[1][1])))
        elif stmt2[0] and v == stmt2[1][1]:
            if v_idx == 0:
                possible.add((stmt[0], (stmt2[1][0], stmt[1][1])))
            else:
                possible.add((stmt[0], (stmt[1][0], stmt2[1][0])))
    return possible


def is_correct(formula):
    """
    Check the logical formula for correctness
    e.g. AND(A==B, B==C, A!=C) is incorrect (absurd)
    """
    if len(set(formula)) < 2: True
    all_eliminations = set()
    for stmt in formula:
        for v in stmt[1]:
            all_eliminations |= (eliminate(formula, stmt, v))
        # if (not stmt[0], stmt[1]) in formula: 
            # return False  # Check for direct contradictions
    for stmt in all_eliminations:
        if (not stmt[0], stmt[1]) in formula: 
            return False  # Check for elimination contradictions
        if (not stmt[0], (stmt[1][1], stmt[1][0])) in formula: return False
    return True


def filter_correct(formulas):
    """
    Given a list of formuals containing statements like (<bool>, (?v1, ?v2)), 
    return only correct formulas
    """
    return set([tuple(x) for x in formulas if is_correct(x)])


def gen_truth_formulas(objects, set_of_constraints=None):
    """
    Given the list of parameters that could potentially be equal to each other
    return a set of formulas that will exhaustively list all feasible eq/neq combinations
    """
    pairs = list(itertools.combinations(objects, r=2))
    truth_table = itertools.product([True, False], repeat=len(pairs))
    possible_formulas = []
    for truth_map in truth_table:
        facts = list(zip(truth_map, pairs))
        if set_of_constraints:
            false_fact = False
            for fact in facts:
                for constraint in set_of_constraints:
                    if (fact[0] != constraint[0] 
                        and (    fact[1]                  == constraint[1]
                             or  (fact[1][1], fact[1][0]) == constraint[1])):
                        false_fact = True
                        break
                if false_fact:
                    break
            if false_fact:
                continue
        possible_formulas.append(facts)
        # possible_formulas.append(list(zip(truth_map, pairs)))
    return filter_correct(possible_formulas)


def gen_combined_truth_table(multiple_formula_sets, ini_constraints=None):
    """
    Generate complete set of possible combinations of all equality formulas in form:
    [
        [[(True (?v1, ?v2)) (False (?v2, ?v3)), ...], [...]],
        [[(True (?v4, ?v5)) (False (?v6, ?v5)), ...], [...]]
    ]
    =>
    combine each of the formulas with each other formula from other list:
    Example:
    [["A", "B", "C"], ["X", "Y"]] 
    =>
    [('A', 'X'), ('A', 'Y'), ('B', 'X'), ('B', 'Y'), ('C', 'X'), ('C', 'Y')]
    """
    all_sets = [gen_truth_formulas(x, ini_constraints) for x in multiple_formula_sets]
    return [l1_flatten(x) for x in itertools.product(*all_sets)]


def gen_grouped_truth_table(multiple_formula_sets, ini_constraints=None):
    """
    Same as gen_combined_truth_table but rather generates grouped (non-flattened) variable truth statemets
    """
    all_sets = [gen_truth_formulas(x, ini_constraints) for x in multiple_formula_sets]
    return list(itertools.product(*all_sets))


def generate_transitive_replacement_map(comparison_group):
    """Generate a map of what to replace with what from comparison group of IDs, given the transitivity of equality
    Required format of IDs is ?ClassName-<NUM> where <NUM> is parameter order by occurence

    Args:
        comparison_group (list of tuples of truth,param_pair): a comparison group to convert to replacement dict

    Returns:
        dict: replacement dict of each paramenter name to which it equals
        like {"?v-3": "?v-1", "?v-4": "?v-1"}
    """
    gl = [set(p[1]) for p in comparison_group if p[0]]
    groups = []
    for expr in gl:
        found = False
        for g in groups:
            if g.intersection(expr):
                g |= expr
                found = True
        if not found:
            groups.append(expr)
    groups = [sorted(list(x), key=lambda x: int(x.split("-")[-1])) for x in groups]
    total_equality_map = {}
    for sorted_equality_group in groups:
        equality_map = {}
        equal_to = sorted_equality_group[0]
        for var in sorted_equality_group[1:]:
            equality_map[var] = equal_to
        total_equality_map.update(equality_map)
    return total_equality_map


def cached_id(hcp):
    global HCPCACHE
    if not id(hcp) in HCPCACHE:
        HCPCACHE[id(hcp)] = hcp._self_id()
    return HCPCACHE[id(hcp)]
sid = cached_id


def is_possible(warrants, op, hcp1, hcp2):
    "return if we have any warrants that prevent this branch from materializing"
    if op == "==":
        not_op = "!="
    elif op == "!=":
        not_op = "=="
    else:
        raise AssertionError("op "+op)
    if (sid(hcp1), sid(hcp2),) in warrants[not_op] or \
        (sid(hcp2), sid(hcp1),) in warrants[not_op]:
        return False
    return True


def is_obvious(warrants, op, hcp1, hcp2):
    "check if this branch is already obvious and no need to generate a new one"
    if (sid(hcp1), sid(hcp2),) in warrants[op] or \
        (sid(hcp2), sid(hcp1),) in warrants[op]:
        return True
    return False


def generate_potentially_equal_objects(schema):
    """returns grouped probable parameter equality maps in form of ((True/False ("?v-1", "?v-2")), ...), ...
    and
    replacements maps (non-grouped)

    Args:
        schema (list): a list - stack of operators from symex

    Returns:
        tuple: grouped eqs list, replacement map list
        returned tuples are positionally-synchronised
    """
    warrants = defaultdict(set)
    set_events = defaultdict(list)
    set_attrs_per_class = defaultdict(set)
    classes_counter = defaultdict(dict)
    instantiations = set()
    for a in schema:
        if a[0] == "op_eq":
            warrants["=="].add((a[1]._self_id(), a[2]._self_id()))
        elif a[0] == "op_neq":
            warrants["!="].add((a[1]._self_id(), a[2]._self_id()))
        elif a[0] == "op_ensure_neq":
            warrants["!="].add((a[2]._self_id(), a[3]._self_id()))
        elif a[0] == "op_setattr": # or a[0] == "op_getattr":
            # FIXME: set_attrs_... is now ANY access
            # because any constraint may be broken too
            hcp_obj = a[1]
            if hcp_obj._self_class in hyperc.world.SPECIAL_CLASSES:
                continue  # Ignore special classes like SumResult
            name = a[2]
            pname = f"{hcp_obj._self_class_id()}-{name}"
            if hcp_append_if_not(set_events[pname], hcp_obj):
                set_attrs_per_class[hcp_obj._self_class].add(name)
        # TODO: now check if we have a read after write
        elif a[0] == "op_getattr":
            hcp_obj = a[1]
            if hcp_obj._self_class in hyperc.world.SPECIAL_CLASSES:
                continue  # Ignore special classes like SumResult
            name = a[2]
            pname = f"{hcp_obj._self_class_id()}-{name}"
            if pname in set_events:
                if hcp_append_if_not(set_events[pname], hcp_obj):
                    set_attrs_per_class[hcp_obj._self_class].add(name)
        elif a[0] == "op_instantiate":
            instantiations.add(a[2]._self_id())

        for v in a[1:]:
            if isinstance(v, hc.HCProxy) or isinstance(v, hc.HCShadowProxy):
                if v._self_wrapped is None:
                    classes_counter[v._self_class][v._self_id()] = v
        v = a[1]

    # 1. detect if we have duplicate classes
    # 2. for every duplicate class, check if we do same-attr operations
    # 3. then just branch for if they same or not
    # 4. after completion of entire operation - prune absurd/duplicate branches

    potentially_equal_to_be_taken_care_of = set()
    parameter_id_map = {}

    for cls_, parms in classes_counter.items():
        parms = {k: v for k, v in parms.items() if not k in instantiations}
        if len(parms) < 2: 
            # print("RWB: Classes not 2", parms)
            continue  # only continue if more than one param of this class exists
        for name in set_attrs_per_class[list(parms.values())[0]._self_class]:  # all used attrs of this class
            pname = f"{list(parms.values())[0]._self_class_id()}-{name}"
            if len(set_events[pname]) > 1:  # we got potential rewrite event on this attr
                # print(">>>> DEALING WIH", pname)
                for v in parms.values():
                    parameter_id_map[v._self_id()] = v
                potentially_equal_to_be_taken_care_of.add(tuple(sorted([v._self_id() for v in parms.values()])))
            else:
                # print("RWB: REWRITES NOT 2", parms)
                pass
    # id_parameter_map = {v: k for k, v in parameter_id_map.items()} 
    # print("RWB2>>> ID MAP:", parameter_id_map)
    # print("RWB2>>> ALL POTENTIAL PARAMS", potentially_equal_to_be_taken_care_of)
    # print("RWB2>>> COMBINED TT", gen_combined_truth_table(potentially_equal_to_be_taken_care_of))
    # print("RWB2>>> COMBINED GTT", gen_grouped_truth_table(potentially_equal_to_be_taken_care_of))
    final_tt = list()
    final_replacements = list()  # list of dicts

    global HCPCACHE
    HCPCACHE = {}

    warrant_constraints = set()
    for w_eq in warrants["=="]:
        warrant_constraints.add((True, (w_eq[0], w_eq[1])))
    for w_eq in warrants["!="]:
        warrant_constraints.add((False, (w_eq[0], w_eq[1])))

    grouped_tt = gen_grouped_truth_table(potentially_equal_to_be_taken_care_of, warrant_constraints)
    # progress.info(f"Filtering truth table of {len(grouped_tt)} elements")
    for grouped_logix in grouped_tt:
        ignore = False
        this_replacements = {}
        for logix_group in grouped_logix:
            for stmt in logix_group:
                # FIXME: looks like double-conversion happens below >>>
                hcp_place = parameter_id_map[stmt[1][0]]
                eq_obj = parameter_id_map[stmt[1][1]]
                if stmt[0] == True:
                    if not is_possible(warrants, "==", hcp_place, eq_obj): ignore = True
                    if is_obvious(warrants, "==", hcp_place, eq_obj): ignore = True 
                elif stmt[0] == False:
                    if not is_possible(warrants, "!=", hcp_place, eq_obj): ignore = True
                    if is_obvious(warrants, "!=", hcp_place, eq_obj): ignore = True 
        if not ignore:
            final_tt.append(grouped_logix)
            all_replacements = {}
            for logix_gropup in grouped_logix:
                # create accruate replacement map
                #            replacement map must always replace all objects to their smallest
                #            also do a transitive refactoring
                all_replacements.update(generate_transitive_replacement_map(logix_gropup))
            final_replacements.append(all_replacements)
    return final_tt, final_replacements  # to be zipped
