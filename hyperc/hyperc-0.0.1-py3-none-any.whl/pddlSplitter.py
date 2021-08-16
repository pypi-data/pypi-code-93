import hyperc.exceptions
from hyperc.util import get_work_dir, check_user_disable_execution
import itertools, json, string, re, os, copy
import logging
log = logging.getLogger("hyperc")

import hyperc.pddl as pddl
import hyperc.settings as settings
import re
from os.path import join

POODLE_SPLIT_MATH_LOCK_PREDICATE_NAME = "poodle-split-math-not-in-progress"

class Permutation():
    def __init__(self, type, object_type_amount):
        self.type = type
        self.variable_cellAmount = 0
        self.object_type_amount = object_type_amount
        self.variables = set([])

    def addVar(self, var):
        self.variables.add(var)

    def getPermutation(self):
        return pow(self.object_type_amount, len(self.variables))


class CutFilter:
    def __init__(self, split_skip=1):
        self.split_skip = split_skip  # divisor for modulus
        self.cut_counter = 0

    def filter(self, b: bool):
        if b:
            self.cut_counter += 1
            if self.cut_counter == self.split_skip:
                self.cut_counter = 0
                return True
        return False
    
    def reset(self):
        self.cut_counter = 0

class PrediKnife():
    """
    This cutter use only text representation of predicate
     please pass to cutCheck(self, predicat) predicat with filled fact field
    """
    WAIT = 0
    WORKING = 1
    CUT = 2

    def __init__(
            self,
            cutBy=[['SumResult-[0-9]+-term1', 'SumResult-[0-9]+-term2', 'SumResult-[0-9]+-summ'],
            ['MulResult-[0-9]+-term1', 'MulResult-[0-9]+-term2', 'MulResult-[0-9]+-mul']], SPLIT_SKIP=1):
        """
        example of cut group
        cutBy=[['SumResult-operator2', 'SumResult-operator1', 'SumResult-result'], ['GreaterThan-val1', 'GreaterThan-val2'], ['GreaterEqual-val1', 'GreaterEqual-val2']]
        """
        self.cut_filter = CutFilter(SPLIT_SKIP)
        self.cutBy = cutBy  # cutBY is array of array
        self.flag = "WAIT"
        self.cutGroup = []
        self.catched = []
        self.predicate_counter = 0

    def checkGroup(self):
        if len(self.cutGroup) == len(self.catched):
            if sorted(self.cutGroup) == sorted(self.catched):
                # print("split group ",self.catched ," by ", self.cutGroup)
                self.flag = "WAIT"
                self.catched = []
                self.cutGroup = []
                return True
            else:
                raise hyperc.exceptions.SplitterError("pddl is broken unknown cut group {0}".format(self.catched))
        return False

    def update_action_parameter_list(self, a):
        self.current_action = a
        self.predicate_counter = 0
        self.flag = "WAIT"
        self.catched = []
        self.cutGroup = []
        self.cut_filter.reset()

    def cutCheck(self, predicat):
        self.predicate_counter+=1
        if self.predicate_counter == len(self.current_action.precondition):
            return False
        str = predicat.fact
        if self.flag == "WAIT":
            for cg in self.cutBy:
                for c_regex in cg:
                    if re.match(c_regex, str):
                        self.cutGroup = cg
                        self.catched.append(c_regex)
                        self.flag = "WORKING"
                        # print("WAIT ", c_regex, "  ", str)
                        # print(re.match(c_regex, str))
                        # print(self.catched)
                        return self.cut_filter.filter(self.checkGroup())

        if self.flag == "WORKING":
            for c_regex in self.cutGroup:
                if re.match(c_regex, str):
                    self.catched.append(c_regex)
                    # print("WORKING " ,c_regex, "  ", str)
                    # print(re.match(c_regex, str))
                    # print(self.catched)
                    return self.cut_filter.filter(self.checkGroup())


class KnifeGroundLimit():

    def __init__(self, problem: pddl.Problem = None, ground_limit=400 * 1000, SPLIT_SKIP=1, aggressive=False, forward=True, backward = False):
        log.info("Advanced PDDL splitter load")
        self.ground_limit = ground_limit  # limit for variable permutation
        self.permutations = {}  # dict of class Permutation
        self.problem = problem
        self.predicate_counter = 0
        self.cut_filter = CutFilter(SPLIT_SKIP)  # divisor for modulus
        self.aggressive = aggressive
        self.backward = backward
        self.forward = forward

    def update_action_parameter_list(self, action: pddl.Action):
        self.current_action = action
        self.predicate_counter = 0
        # self.set_action_variable_to_objType(self.current_action.parameters)
        self.cut_filter.reset()

    # TODO fixme
    #parameters_list is list following by ":parameters" in pddl (ActionSplitter.parameters)
    def set_action_variable_to_objType(self, parameters_list):
        self.variable_to_objType = {}  # dict[variableName] = objtype
        skip_next = False
        type_next = False
        varName = ""
        for p in parameters_list:
            if p == '-':
                type_next = True
                continue
            if type_next:
                self.variable_to_objType[var_name] = p  # store variable type
                type_next = False
                continue
            var_name = p  # store variable name

# TODO fixme
    # predicate - is line from ":predicate section"
    def calculate_permutation(self, predicate):
        predicate = self.not_unpack(predicate)
        #add new predicate to permutation
        for var in predicate[1:]:
            if not var[0] == '?':
                continue
            if self.variable_to_objType[var] in self.permutations:
                self.permutations[self.variable_to_objType[var]].addVar(
                    var)
            else:
                #TODO check for ZERO type in update_action_parameter_list and multiply by ZERO all result to block splittting
                object_type_amount = 0  # if at least one variable from parameters doesn't has instances all action will be multiply by ZERO check it in next if/else
                # We may have action with variable which doesn't have any object instance in problem.pddl
                if self.variable_to_objType[var] in self.object_type_amount:
                    object_type_amount = self.object_type_amount[self.variable_to_objType[var]]
                # else:
                    self.permutations[self.variable_to_objType[var]] = Permutation(
                        self.variable_to_objType[var],
                        object_type_amount)
                    self.permutations[self.variable_to_objType[var]].addVar(var)
        fullPermutation = 1
        for p in self.permutations:
            fullPermutation *= self.permutations[p].getPermutation()
        return fullPermutation

    # check where I can split (check that at least one variable not found)
    def can_split_here(self, predicate: pddl.Predicate):
        if self.predicate_counter == len(self.current_action.precondition):
            #don't cutoff last predicat it is useless
            return False
        found = False
        for var in predicate.vars:
            for p in self.current_action.precondition[self.predicate_counter:]:
                if p.containVar(var):
                    found = True
                    break
            if not found:
                return True
        return False
        
    # forward check
    def should_split_here(self, predicate: pddl.Predicate):
        if self.predicate_counter == len(self.current_action.precondition):
            #don't cutoff last predicat it is useless
            return False
        for var in predicate.vars:
            for p in self.current_action.precondition[self.predicate_counter:]:
                if p.containVar(var):
                    return False
        return True

    # backward check
    def should_split_here_backward(self, predicate: pddl.Predicate):
        if (self.predicate_counter == 1) or (self.predicate_counter >= len(self.current_action.precondition-1)):
            #don't cutoff first predicat is useless
            return False
        predicate = self.current_action.precondition[self.predicate_counter]
        for var in predicate.vars:
            for p in self.current_action.precondition[0:self.predicate_counter]:
                if p.containVar(var):
                    return False
        return True

    # check where I can split (check that at least one variable not found)
    def can_split_here_backward(self, predicate: pddl.Predicate):
        if self.predicate_counter == 1 or (self.predicate_counter >= len(self.current_action.precondition-1)):
            #don't cutoff first predicat is useless
            return False
        predicate = self.current_action.precondition[self.predicate_counter]
        found = False
        for var in predicate.vars:
            for p in self.current_action.precondition[0:self.predicate_counter]:
                if p.containVar(var):
                    found = True
                    break
            if not found:
                return True
        return False

# V1.3
    def cutCheck(self, predicate: pddl.Predicate):
        self.predicate_counter += 1
        ret = False
        if self.forward:
            if self.aggressive:
                ret = self.can_split_here(predicate)
            else:
                ret = self.should_split_here(predicate)
        if self.backward and (not ret):
            if self.aggressive:
                ret = self.can_split_here_backward(predicate)
            else:
                ret = self.should_split_here_backward(predicate)
        
        return self.cut_filter.filter(ret)


# V2.1
# TODO fixme
    def cut_check_with_permutation(self, predicate: pddl.Predicate):
        self.predicate_counter += 1

        if self.should_split_here(predicate):
            self.permutations = {}
            return True

        permutation = self.calculate_permutation(predicate)
        if permutation > self.ground_limit:
            if self.can_split_here(predicate):
                self.permutations = {}
                return True
            return False
        else:
            return False

class ActionSplitter():

    def __init__(self, domain: pddl.Domain, problem: pddl.Problem = None, ground_limit: int = 100 * 1000, work_dir = None, term_list=None, solver_lock=None):
        self.min_split = 1
        self.SPLIT_SKIP = settings.HYPERC_SPLIT_SKIP
        self.max_effect_amount = settings.HYPERC_MAX_EFFECT_AMOUNT
        self.domain = domain
        self.problem = problem
        self.work_dir = work_dir
        if self.work_dir is None:
            self.work_dir = get_work_dir()
        self.term_list = term_list
        self.solver_lock = solver_lock

        self.all_predicates = []
        for a in self.domain.actions:
            self.all_predicates.extend(a.precondition)
            self.all_predicates.extend(a.effect)

        if settings.HYPERC_DUMP_ORIGIN == '1':
            with open(join(self.work_dir, 'domain_orig.pddl'), 'w') as f:
                f.write(str(self.domain))
            with open(join(self.work_dir, 'problem_orig.pddl'), 'w') as f:
                f.write(str(self.problem))

        self.split_factory = []
        for splitter in settings.HYPERC_SPLIT_STRATEGY.upper().split(';'):
            if "PATTERN_STRATEGY" == splitter:
                self.split_factory.append(PrediKnife(SPLIT_SKIP=self.SPLIT_SKIP))
            if "GROUND_LIMIT" == splitter:
                self.split_factory.append(KnifeGroundLimit(problem=problem, SPLIT_SKIP=self.SPLIT_SKIP))
                # KnifeGroundLimit(problem=problem, SPLIT_SKIP=self.SPLIT_SKIP, backward=True, forward=False)
        if work_dir:
            self.work_dir = work_dir
        counter = 0
        for a in self.domain.actions:
            a.idx = counter
            counter += 1

    def stage_1(self):
        #Stage 1
        #look for splittable action and enumerate actions
        self.splittable_action = {}
        f = open(join(self.work_dir, 'grounding_origin.txt'), 'w')
        grounding_total = 0
        for a in self.domain.actions:
            if a.parameters is None:
                a.generate_parameters()
            grounding = a.grounding_size(self.problem)
            grounding_total += grounding
            f.write(a.name + " " + str(grounding) + '\n')

            log.debug(",".join(map(str,a.parameters)))
            splitMe = 0
            for knife in self.split_factory:
                knife.update_action_parameter_list(a)
                for p in a.precondition:
                    if knife.cutCheck(p):
                        splitMe += 1
                    if splitMe >= self.min_split:  # split less then for 3 chunk is useless
                        break
                if splitMe >= self.min_split:
                    self.splittable_action[a.name] = a
                    break
        f.write("TOTAL " + str(grounding_total) + '\n')
        f.close()

    def stage_1_2(self):
        """
        Delete splittable actions from self.domain.actions
        """
        # I split action on small actions which I named slices or slice of action
        for sa in self.splittable_action:
            self.domain.actions.remove(self.splittable_action[sa])

    def stage_2(self):
        # Stage 2
        # store splices here
        self.action_slices = {}
        for a_name in self.splittable_action:
           self.action_slices[a_name] = [self.splittable_action[a_name]]
        for knife in self.split_factory:
            for a_name in self.action_slices:
                swap_slices = []
                for idx, a in enumerate(self.action_slices[a_name]):
                    knife.update_action_parameter_list(a)
                    counter = 0
                    # costs ! First slice is copy from origin the others are zero
                    slice_of_action = pddl.Action(f"{a.name}-{counter}-{knife.__class__.__name__}",
                        parameters=None, cost=a.cost,
                        cost_target=a.cost_target, idx=counter, parent=self.splittable_action[a_name])
                    orig_precondition = copy.copy(a.precondition)
                    for p in a.precondition:
                        slice_of_action.precondition.append(p)
                        if knife.cutCheck(p):
                            for del_p in slice_of_action.precondition:
                                orig_precondition.remove(del_p)
                            swap_slices.append(slice_of_action)
                            counter += 1
                            slice_of_action = pddl.Action(f"{a.name}-{counter}-{knife.__class__.__name__}", parameters=None,
                                                    cost=0, cost_target=a.cost_target, idx=counter,
                                                    parent=self.splittable_action[a_name])
                    if counter > 0:
                        swap_slices.append(slice_of_action)
                    else:
                        swap_slices.append(a)

                self.action_slices[a_name] = swap_slices



    def stage_3_1(self, a_name):
        # Stage3-1
        # arrange effect
        a = self.splittable_action[a_name]
        consumedEffects = []
        # do effect in last slice with coresponding variable from lat to first
        for slice in reversed(self.action_slices[a.name]):
            for eff in a.effect:
                useFullEffect = False
                vars = eff.getVars()
                for par in vars:
                    if slice.containVar(par):
                        useFullEffect = True
                        break
                if useFullEffect:
                    if eff not in consumedEffects:
                        consumedEffects.append(eff)
                        slice.effect.append(eff)
        for eff in a.effect:
            if eff not in consumedEffects:
                consumedEffects.append(eff)
                self.action_slices[a.name][-1].effect.append(eff)

    def split_effect_stage_3_2(self, a_name):
        #   Stage 3-2
        #      Split effects
        arr = self.action_slices[a_name]
        loopCondition = True
        while loopCondition:
            loopCondition = False
            for idx, slice in enumerate(arr):
                if len(slice.effect) > self.max_effect_amount:
                    loopCondition = True
                    lenght = len(slice.effect)
                    sAmount = lenght / self.max_effect_amount if lenght % self.max_effect_amount == 0 else(
                        lenght / self.max_effect_amount) + 1
                    # last_hope = slice.precondition[-1].vars
                    for count in range(0, int(sAmount) + 1):
                        ac = pddl.Action("{0}-{1}-{2}-eff".format(slice.name, slice.idx, count), parameters=None)
                        startFrom = 0
                        for subCounter in range(self.max_effect_amount):
                            if len(slice.effect) == startFrom: break
                            # last hope move seems useless
                            # if len(slice.effect) > startFrom + 1:
                            #     for var in last_hope:
                            #         if slice.effect[startFrom].containVar(var):
                            #             startFrom += 1
                            #             break
                            ac.effect.append(slice.effect[startFrom])
                            del(slice.effect[startFrom])
                        if len(ac.effect) > 0:
                            arr.insert(idx + count + 1, ac)
                if loopCondition: break

        # fix enumerator
        for idx, a in enumerate(arr):
            a.idx = idx
            a.parent = self.splittable_action[a_name]

    def stage_3_4(self, a_name):
        # Stage 3-4
        # export usefull parameters(variables) for next sliced action sequence
        arr = self.action_slices[a_name]
        for idx, slice in enumerate(arr):
            # log.debug("Export from %s", slice.name)
            # print("Export from %s", slice.name)
            if (idx + 1) == len(arr):
                break
            arrNext = arr[idx+1:len(arr)]
            for idxNext, sliceNext in enumerate(arrNext):
                export = pddl.Predicate(fact="from-{0}-to-{1}".format(arr[idx].name, arr[1 + idx + idxNext].name))
                # iterate list of slice's parameters and export(in effect) and import in next slice
                for var in slice.get_vars():
                    if export.containVar(var): # prevent double export
                        continue
                    if sliceNext.containVar(var):
                        export.vars.append(var)
                # skip blank predicates
                if len(export.vars) == 0:
                    continue
                export_negated = pddl.Predicate(fact=export.fact, vars=export.vars, negated=True, alien=True)
                # cont = False
                # #skip duplicates
                # for effA in slice.effectAppend:
                #     if isinstance(effA, list):
                #         if effA[1:] == sliceEffectAppend[1:]:
                #             tmplist = []
                #             tmplist.append(effA[0])
                #             tmplist.extend(sliceEffectAppend[1:])
                #             sliceNext.preconditionPrepend.append(tmplist)      # full predicate
                #             notP = "(not %s)" % list_to_lisp(tmplist)
                #             # delete duplicated (not %s ) from history
                #             for ggSlice in arr[0:1+idx+idxNext]:
                #                 for eA in ggSlice.effectAppend:
                #                     if eA == notP:
                #                         ggSlice.effectAppend.remove(eA)
                #             sliceNext.effectAppend.append(notP)
                #             cont = True
                # if cont :
                #     continue
                slice.effect.append(export)                            # full predicate
                # should prepend exported to select it first
                sliceNext.precondition.insert(0, export)
                # append deleting of imported predicate as negative predicate
                sliceNext.effect.append(export_negated)

    def fill_parameters_for_dummy(self, a_name):
        for slice in self.action_slices[a_name]:
            if slice.parameters is None:
                slice.parameters=[]
            for var in slice.get_vars():
                for par in slice.parent.parameters:
                    if par.var == var:
                        slice.parameters.append(par)

    def fill_predicate_declaration_for_dummy(self):
        for a in self.domain.actions:
            for p in a.precondition:
                if not p.fact in self.domain.get_predicate_declaration_names():
                    pd = pddl.PredicateDeclaration(fact=p.fact)
                    self.domain.predicates.append(pd)
                    for v in p.vars:
                        for par in a.parameters:
                            if par.var == v:
                                pd.vars.append(pddl.Parameter(var=f'?var{len(pd.vars)}', type=par.type))
                    
                            

    def do_snake_stage_3_6(self, a_name):
        # Stage 3-6
        # Fourth step do snake
        arr = self.action_slices[a_name]
        for idx, slice in enumerate(arr):
            if idx > 0:
                slice.effect.append(pddl.Predicate(fact="snake-{0}-step-{1}".format(a_name, idx), negated=True))
                slice.precondition.insert(0, pddl.Predicate(fact="snake-{0}-step-{1}".format(a_name, idx)))
            if idx < (len(arr) - 1):
                slice.effect.append(pddl.Predicate(fact="snake-{0}-step-{1}".format(a_name, idx + 1)))
        
    def math_lock_stage_3_7(self, a_name):
        # Stage 3-7
        # close the snake first with last in goal
        arr = self.action_slices[a_name]
        math_lock = pddl.Predicate(fact=POODLE_SPLIT_MATH_LOCK_PREDICATE_NAME)
        math_lock_negated = pddl.Predicate(fact=POODLE_SPLIT_MATH_LOCK_PREDICATE_NAME, negated=True)
        arr[0].precondition.insert(0, math_lock)
        arr[0].effect.append(math_lock_negated)
        arr[-1].effect.append(math_lock)

        # Working lock loop first with last
        working = pddl.Predicate(fact=f"working-{a_name}")
        working_negated= pddl.Predicate(fact=working.fact, negated=True)
        arr[0].precondition.insert(0, working_negated)
        arr[0].effect.append(working)
        arr[-1].effect.append(working_negated)


    def math_lock_insert_precond(self):
        self.problem.goal.insert(0, pddl.Predicate(fact=POODLE_SPLIT_MATH_LOCK_PREDICATE_NAME))
        self.problem.init.append(pddl.Predicate(fact=POODLE_SPLIT_MATH_LOCK_PREDICATE_NAME))
        for a in self.domain.actions:
            a.precondition.insert(0, pddl.Predicate(fact=POODLE_SPLIT_MATH_LOCK_PREDICATE_NAME))

    def insert_actions_stage_4(self):
        # Stage 3-8
        # Insert
        count = 0
        for a_name in self.splittable_action.keys():
            for slice in self.action_slices[a_name]:
                self.domain.actions.insert(slice.parent.idx+count, slice)
                count +=1
            count -= 1
        
    def insert_poodle_split_fact(self):
        poodle_math_pred = pddl.Predicate(fact=POODLE_SPLIT_MATH_LOCK_PREDICATE_NAME)
        psm_sig = poodle_math_pred.get_signature()
        self.domain.predicates.append(psm_sig)


    def split(self):
        self.stage_1()

        self.stage_1_2()

        self.stage_2()

        # Stage 3 (fix chunks)
        for a_name in self.action_slices:
            check_user_disable_execution(self.solver_lock)
            self.stage_3_1(a_name)
            check_user_disable_execution(self.solver_lock)
            # Split effects
            self.split_effect_stage_3_2(a_name)
            check_user_disable_execution(self.solver_lock)
            self.stage_3_4(a_name)
            check_user_disable_execution(self.solver_lock)
            self.do_snake_stage_3_6(a_name)
            check_user_disable_execution(self.solver_lock)
            self.math_lock_stage_3_7(a_name)
            
            if self.domain.dummy:
                self.fill_parameters_for_dummy(a_name)

        self.math_lock_insert_precond()
            # else:
            #     # TODO HERE: append to every precondition (not (poodle-split-math-in-progress))
            #     CHECKME MAY be useless!!!!
            #     if len(splittedAction): self.all_actions[an].precondition.insert(0,f"({POODLE_SPLIT_MATH_LOCK_PREDICATE_NAME})")
            #     combined_actions.append(str(self.all_actions[an]))

        self.insert_actions_stage_4()
        # self.insert_poodle_split_fact()
        if self.domain.dummy:
            self.fill_predicate_declaration_for_dummy()
        else:
            predicate_declaration = list()
            grounding_total = 0
            f = open(join(self.work_dir, 'grounding_splitted.txt'), 'w')
            for act in self.domain.actions:
                for predicate in itertools.chain(act.precondition, act.effect):
                    p = predicate.get_signature()
                    if p not in predicate_declaration:
                        predicate_declaration.append(p)
                if act.parameters is None:
                    act.generate_parameters()
                grounding = act.grounding_size(self.problem)
                grounding_total += grounding
                f.write(act.name + " " + str(grounding) + '\n')
            f.write("TOTAL " + str(grounding_total) + '\n')
            f.close()
            self.domain.predicates = list(predicate_declaration)

        #splitter self test
        check_list = []
        for a in self.domain.actions:
            for predicate in itertools.chain(a.precondition, a.effect):
                check_list.extend(a.precondition)
                check_list.extend(a.effect)
        for p in self.all_predicates:
            assert p in check_list

        dp = pddl.FullDomain(self.domain, self.problem, term_list=self.term_list, solver_lock=self.solver_lock)
        if hasattr(self, "work_dir"):
            dp.work_dir = self.work_dir
        return dp
