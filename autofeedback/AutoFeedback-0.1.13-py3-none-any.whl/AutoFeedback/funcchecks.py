import importlib

def exists(funcname,modname=None):
    import inspect
    if not modname:
        mod = importlib.import_module('main')
    else:
        mod=modname
    funcstring="mod."+funcname # get variable from main code
    try:
        testfunc=eval(funcstring)
        return(inspect.isfunction(testfunc))
    except:
        return (False)

def get_func(funcname,modname=None):
    if not modname:
        mod = importlib.import_module('main')
    else:
        mod=modname
    funcstring="mod."+funcname # get function from main code
    return(eval(funcstring))

def input_vars(func,inputs):
    try:
        if hasattr(inputs,"__len__"):
            func(*inputs)
        else:
            func(inputs)
        return True
    except TypeError:
        return (False)
    
def returns(func,inputs):
    try:
        if hasattr(inputs,"__len__"):
            res=func(*inputs)
        else:
            res=func(inputs)
        if hasattr(res,"__len__"):
            res=list(res)
        return (res!=None)
    except:
        return False

def check_outputs(func,inputs,expected):
    from AutoFeedback.varchecks import check_value
    try:
        res=func(*inputs)
        if hasattr(expected, "check_value") and callable(expected.check_value) : return expected.check_value(res)
        else : return (check_value(res,expected))
    except:
        return False


def check_calls(func,inputs,call):
    import inspect
    import ast
    try:
        all_names = [c.func for c in ast.walk(ast.parse(inspect.getsource(func))) if isinstance(c,ast.Call)]
        call_names = [l.id for l in all_names if isinstance(l,ast.Name)]
        return (call in call_names)
    except:
        return False


def check_func(funcname,inputs,expected,calls=[],modname=None,output=True):
    from AutoFeedback.function_error_messages import print_error_message
    call=[]
    ins=inputs[0]
    outs=expected[0]
    res = -999
    try:
        assert(exists(funcname,modname)), "existence"
        func=get_func(funcname,modname)
        assert(input_vars(func,inputs[0])), "inputs"
        
        assert(returns(func,inputs[0])), "return"
        for ins,outs in zip(inputs,expected):
            res=func(*ins)
            assert(check_outputs(func,ins,outs)), "outputs"
        for call in calls:
            assert(check_calls(func,inputs[0],call)), "calls"
        if output: print_error_message("success",funcname)
    except AssertionError as error:
        if output: print_error_message(error,funcname,inp=ins,exp=outs,result=res,callname=call)
        return(False)
    except:
        if output: print_error_message("execution",funcname,inp=ins)
        return(False)

    return(True)



