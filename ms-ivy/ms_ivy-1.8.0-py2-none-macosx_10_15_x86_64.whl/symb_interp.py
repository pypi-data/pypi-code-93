#
# Symbolic interrpreter for Ivy
#

import ivy_logic as il
import ivy_module as im
import ivy_actions as ia

# Continuations

class Continuation(object):
    def __init(self,code):
        self.binding = dict()     # variable binding
        self.code = code          # code to execute


# Program state
#

class State(object):
    def __init__(self,code):
        self.constraint = il.true   # the state constraint
        self.binding = dict()       # the variable binding
        self.continuations = [Continuation(code)]          # stack of continuations


# Process state

class ProcessSate(object):
    def __init__(self,code):
        self.states = [State(code)]

# Execute code from state until stopping point.
# Parameters:
#
# ctx : execution context
# st : initial state
#
# Returns: list of State


def assign_action_symex(self,ctx,st):
    update_binding(st.binding,self.lhs(),self.rhs())
    
ia.AssignAction.symex =  assign_action_symex

b*def do_assign(binding,lhs,rhs):
    n = lhs.rep
    fields = []
    while lhs.rep in ivy_module.module.destructor_sorts:
        fields.append(lhs)
        lhs = lhs.args[0]
    argvals = [eval_in_binding(binding,x) for x in lhs.args]
    def recur(idx,val):
        if idx == 0:
            return eval_in_binding(binding,rhs)
        idx -= 1
        field = fields[idx]
        argvals = [eval_in_binding(binding,x) for x in field.args[1:]]
        fval = val.get(field.rep)
        res = recur(idx,fval(*argvals))
        return val.update(field.rep,fval.update(argvals,res))
    res = recur(len(fields),binding.get(lhs.rep)(*argvals))
    return binding.update(lhs.rep,res)
        
            
