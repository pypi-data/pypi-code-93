import itertools
import hyperc.poc_symex as psx
from collections import defaultdict
import logging
progress = logging.getLogger("hyperc_progress")

# implementation strategy:
# Stage 1: just delete unused predicates from effect (negated too!)
# Stage 2: for *-hcsystem-is-free, delete negated effect too
#          find variable name for predicate being deleted, delete -free predicate if present
#          also delete the precondition predicate -is-free
# Stage 3: remove math operarion if it is safe:
#          Mul, Div, Sum - may be removed if the result is not used anywhere else
# Stage 4: remove associated operations for object assignment - warrant is needed!
#          - check if we have a warrant that value is always present (may indirectly acquire by checking for novalue preds)
#          - delete variable selection from preconditions if allowed (for math and assignments)
#          trace if variables are used in math operations
#          delete these math operations if result is only used in effect assignment
# == we are here ==
#          we work/update predicate with a statically referenced object that is not being used after
#          - same, but with object referenced from module/selected in a certain way that is never selected after
# Stage 5:? detect if this effect is used in another side effect
#          - this effect may be used in a different action but with same fasion - just to rewrite the old value with math stuff
# Stage 6: Remove the selects with warrants
# 
# THE PROBLEM with ASE in general is that if we extend the "inner effect" and "after effect" we could "cancel" the entire program
#             which makes further optimizations impossible as information gets lost (in extreme case the program is known and nothing is computed)

#    ,(   ,(   ,(   ,(   ,(   ,(   ,(   ,(
# `-'  `-'  `-'  `-'  `-'  `-'  `-'  `-'  `

# TODO: use p.fact instead of str(p.get_signature()) - much faster

def remove_side_effects(actions):
    # let's remove add_row first.
    progress.info("Detecting and removing side effects")
    preconditions_used = get_used_predicates(actions)
    action_precond_signatures = get_action_precond_signatures(actions)
    side_effect_candidates = {act: set() for act in actions}
    for act in actions:
        effect_predicates = set([str(p.get_signature()) for p in act.effect])
        unused_effect_predicates = effect_predicates - preconditions_used
        # Stage 1. Clear effects of unused predicates
        new_effect = []
        deleted_predicates = []
        for p in act.effect:
            if not str(p.get_signature()) in unused_effect_predicates:
                new_effect.append(p)
            else:
                deleted_predicates.append(p)
        act.effect[:] = new_effect
        # find is-free predicates in deleted:
        deleted_vars = []
        for p in deleted_predicates:
            deleted_vars.extend([x._self_id() for x in p.vars if x._self_id().startswith("?")])
        # Stage 2. clean preconsitions & hc-free effects
        delete_stale_math_groups(act, deleted_vars, deleted_predicates)
        
        # 1. [SKIP Detect side-effect candidates (int-*, pair of effects)]
        # *. Count amount of uses of effect variables sans the select predicate in same action and sans MATH ops
        #    if count is 1, mark the action as candidate
        for p in act.effect:
            if len(p.vars) != 2: continue 
            # candidate is math only:
            pv1id = p.vars[1]._self_id()
            if not pv1id.startswith("?int-"): continue
            effect_var_uses = var_usage(act.precondition, [], set([p.fact]), skip_math=True)
            pred_sig = str(p.get_signature())
            total_usage = 0
            for pp in act.precondition:
                if str(pp.get_signature()) == pred_sig: 
                    total_usage += len(effect_var_uses[pp.vars[1]._self_id()])
            if total_usage == 0:
                side_effect_candidates[act].add(pred_sig)
        # *. Check that this predicate is not used anywhere except for [this action and] other side-effect candidates for this predicate
        #       (actually, no need to ignore this action as it will already be in candidates for this pred removal)
        #    - if used anywhere where it is not candidate for deletion - remove from candidates
    for act in actions:
        math_groups_map = get_math_group_map(act)
        delete_side_effects = []
        for p in act.effect:
            if len(p.vars) != 2: continue 
            # candidate is math only:
            if not p.vars[1]._self_id().startswith("?int-"): continue
            # *. mark for deletion if count of uses of variable is 1:
            this_effect_var_uses = var_usage(act.precondition, [], set([p.fact]), skip_math=True)
            pred_sig = str(p.get_signature())
            total_usage = 0
            for pp in act.precondition:
                if str(pp.get_signature()) == pred_sig: 
                    total_usage += len(this_effect_var_uses[pp.vars[1]._self_id()])
            if total_usage > 0: continue
            p_sig = str(p.get_signature())
            candidate = True
            for act2 in side_effect_candidates:
                if p_sig in action_precond_signatures[act2] and p_sig not in side_effect_candidates[act2]:
                    candidate = False
                    break
            if candidate:
                delete_side_effects.append(p)
        math_groups = get_math_groups(act)
        # *.1 delete effect, precond and entire math group with this variable
        for p in delete_side_effects:
            act.effect.remove(p)
            if p.vars[1]._self_id() in math_groups_map:
                all_math_vars_clean = True
                varcnt_math = var_usage(pred_list=itertools.chain(act.precondition, act.effect), 
                            skip_predicates=deleted_predicates, skip_math=True) # count use of every variable anywhere except deleted
                for p_mg in math_groups[math_groups_map[p.vars[1]._self_id()]]:
                    if len(varcnt_math[p_mg.vars[1]._self_id()]) != 0:
                        all_math_vars_clean = False
                        break
                if all_math_vars_clean:
                    for p in math_groups[math_groups_map[p.vars[1]._self_id()]]:
                        if p in act.precondition:
                            act.precondition.remove(p)
                        if p in act.effect:
                            act.effect.remove(p)

        # *. continue with free-var math cleanup from above
        delete_stale_math_groups(act, deleted_vars, deleted_predicates)

        # TODO: try with cache enabled!! -- takes too long on symex
        # Now delete stale hcsystem-is-free selects
        hc_var_uses = var_usage(itertools.chain(act.precondition, act.effect), [], set([]), skip_math=False)
        hc_remove = []
        for p in itertools.chain(act.precondition, act.effect):
            if p.name == "hcsystem-is-free" and len(hc_var_uses[p.vars[0]._self_id()]) <= 5:
                hc_remove.append(p)
            if p.name == "hcsystem-is-free-current" and len(hc_var_uses[p.vars[0]._self_id()]) <= 5:
                hc_remove.append(p)
            if p.name == "hcsystem-is-free-next" and len(hc_var_uses[p.vars[0]._self_id()]) <= 5:
                hc_remove.append(p)
            # TODO: what to do with hcsystem-is-free-next ?? we have two parameters? need to remove whole group
        for p in hc_remove:
            if p in act.precondition: act.precondition.remove(p)
            if p in act.effect:
                act.effect.remove(p)


def get_math_groups(act):
    return get_math_groups_in_list(act.precondition) 


def get_math_groups_in_list(p_list):
    math_groups = defaultdict(list) # varname-precicates
    for p in p_list:
        if (p.fact[:9] in ["SumResult", "MulResult", "DivResult"]):
            math_groups[p.vars[0]._self_id()].append(p)
    return math_groups


def get_math_group_map(act):
    mpmap = {}
    for p in act.precondition:
        if (p.fact[:9] in ["SumResult", "MulResult", "DivResult"]):
            mpmap[p.vars[1]._self_id()] = p.vars[0]._self_id()
    return mpmap


def var_usage(pred_list, skip_predicates, skip_factnames=None, skip_math=False):
    varcnt = defaultdict(list)
    pred_list = list(pred_list)
    skip_factnames = skip_factnames or set()
    math_groups = get_math_groups_in_list(pred_list)
    for p in pred_list:
        if p in skip_predicates or p.fact in skip_factnames: 
            continue
        if skip_math and p.fact[:9] in ["SumResult", "MulResult", "DivResult"]:
            # We can only skip math if all variables of math come from other math
            # or from skip predicates
            math_clean = True
            for mp in math_groups[p.vars[0]._self_id()]:
                # Check if this variable is used anywhere but math and ignored
                for m_pl in pred_list:
                    if m_pl in skip_predicates or m_pl.fact in skip_factnames:
                        continue
                    if m_pl.fact[:9] in ["SumResult", "MulResult", "DivResult"]: 
                        continue
                    for v in m_pl.vars:
                        if v._self_id() == mp.vars[1]._self_id():
                            math_clean = False
                            break
                    if math_clean == False: break
                if math_clean == False: break
            if math_clean: continue
        for v in p.vars:
            vid = v._self_id()
            if not vid.startswith("?"): continue
            varcnt[vid].append(p)
    return varcnt


def get_used_predicates(actions, except_action=None):
    preconditions_used = set()
    for act in filter(lambda x: x != except_action, actions):
        for p in act.precondition:
            preconditions_used.add(str(p.get_signature()))
        for p in act.effect:
            if p.fact=="MagicGoal":
                preconditions_used.add(str(p.get_signature()))
    return preconditions_used


def delete_stale_math_groups(act, deleted_vars, deleted_predicates):
    while True: # delete math groups until nothing can be deleted
        hc_free_delete = []
        math_groups = get_math_groups(act)
        varcnt = var_usage(pred_list=itertools.chain(act.precondition, act.effect), 
                            skip_predicates=deleted_predicates, skip_math=True) # count use of every variable anywhere except deleted
        for p in itertools.chain(act.precondition, act.effect):
            # if p.name == "hcsystem-is-free" and p.vars[0]._self_id() in deleted_vars:
                # hc_free_delete.append(p)
            if (p.fact[:9] in ["SumResult", "MulResult", "DivResult"] 
                    and p.vars[1]._self_id() in deleted_vars
                    and len(varcnt[p.vars[1]._self_id()]) == 0):
                    # before deletion - for how many times it is used
                all_math_vars_clean = True
                for p_mg in math_groups[p.vars[0]._self_id()]:
                    if len(varcnt[p_mg.vars[1]._self_id()]) != 0:
                        all_math_vars_clean = False
                        break
                if all_math_vars_clean == True:
                    for p_mg in math_groups[p.vars[0]._self_id()]:
                        hc_free_delete.append(p_mg)
        for p in hc_free_delete:
            if p in act.precondition:
                act.precondition.remove(p)
            if p in act.effect:
                act.effect.remove(p)
            deleted_vars.extend([x._self_id() for x in p.vars if x._self_id().startswith("?")])
        if not hc_free_delete:
            break


def get_action_precond_signatures(actions):
    action_precond_signatures = defaultdict(set)
    for act in actions:
        for p in act.precondition:
            action_precond_signatures[act].add(str(p.get_signature()))
    return action_precond_signatures



