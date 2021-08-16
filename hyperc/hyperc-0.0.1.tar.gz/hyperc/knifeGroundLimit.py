import itertools
import json
import string
import re
import logging
logger = logging.getLogger("hyperc")

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

class KnifeGroundLimit():

    def __init__(self, problem, ground_limit=400 * 1000, parameters_list=None):
        logger.debug("Advanced PDDL splitter load")
        self.ground_limit = ground_limit # limit for variable permutation
        self.permutations = {}  # dict of class Permutation
        self.problem = problem #list of lisp
        self.set_object_type_amount(problem)
        self.predicate_counter = 0
        if parameters_list is not None:
            self.set_action_variable_to_objType(parameters_list)

    def update_action_parameter_list(self, parameters_list, allPredicates):
        self.allPredicates = allPredicates
        self.predicate_counter = 0
        self.set_action_variable_to_objType(parameters_list)

    #parameters_list is list following by ":parameters" in pddl (ActionSplitter.parameters)
    def set_action_variable_to_objType(self, parameters_list):
        self.variable_to_objType = {} #dict[variableName] = objtype
        skip_next = False
        type_next = False
        varName = ""
        for p in parameters_list:
            if p == '-':
                type_next = True
                continue
            if type_next:
                self.variable_to_objType[var_name] = p  #store variable type
                type_next = False
                continue
            var_name = p  # store variable name

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
                object_type_amount = 0 # if at least one variable from parameters doesn't has instances all action will be multiply by ZERO check it in next if/else
                if self.variable_to_objType[var] in self.object_type_amount: #We may have action with variable which doesn't have any object instance in problem.pddl
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


    def set_object_type_amount(self, problem):
        problem_list = problem[0]
        self.object_type_amount = {}  # store here object amount objects per types
        assert problem_list[3][0] == ':objects', problem_list[3]
        object_list = problem_list[3][1:]
        skip_next = False
        counter = 0
        for idx, val in enumerate(object_list):
            if skip_next:
                skip_next = False
                continue
            if val == '-':
                self.object_type_amount[object_list[idx + 1]] = counter
                counter = 0
                skip_next = True
                continue
            counter += 1

        # print(self.object_type_amount)
    # check where I can split
    def can_split_here(self, predicate):
        if self.predicate_counter == len(self.allPredicates):
            #don't cutoff laste predicat it is useless
            return False
        predicate = self.not_unpack(predicate)
        found = False
        for var in predicate[1:]:
            for p in self.allPredicates[self.predicate_counter :]:
                p = self.not_unpack(p)
                if var in p:
                    found = True
                    break
            if not found:
                return True
            #found = False # TODO if uncommetn grounded fact space grow up dramaticaly WHY?
        return False

    def should_split_here(self, predicate):
        if self.predicate_counter == len(self.allPredicates):
            #don't cutoff laste predicat it is useless
            return False
        predicate = self.not_unpack(predicate)
        found = False
        for var in predicate[1:]:
            for p in self.allPredicates[self.predicate_counter:]:
                p = self.not_unpack(p)
                if var in p:
                    return False
        return True

    def not_unpack(self, predicate):
        if predicate[0] == 'not':
                return predicate[1]
        return predicate

# cut before
    def cutCheck(self, predicate):
        self.predicate_counter += 1
        
        return self.should_split_here(predicate)

#TODO next code skipped 

        permutation = self.calculate_permutation(predicate)
        # print(permutation)
        # print(predicate)
        if permutation > self.ground_limit:
            # print(permutation)
            # print(predicate)
            # print(self.variable_to_objType)
            if self.can_split_here(predicate):
                self.permutations = {}
                return True
            return False
        else:
            return False
