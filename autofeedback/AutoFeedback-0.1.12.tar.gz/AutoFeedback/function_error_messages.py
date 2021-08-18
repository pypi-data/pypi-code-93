from __future__ import print_function
import sys

def existence_error(varname):
    error_message="The function " + varname +" does not exist" +"""
    Ensure you have named the function properly,
    bearing in mind that capital letters matter.
    Also ensure that you have used the proper syntax 
    for the definition of a function, i.e. 
        def function_name(inputs):
            ...
    """
    return(error_message)

def input_error(varname,numargs):
    error_message="The function " + varname +" does not accept input correctly\n\
    The function is supposed to accept "+str(numargs)+" input argument(s)."+"""
    Ensure you have specified the input arguments in the function definition. i.e.
        def function_name(input_1, input_2, ...):
            ...
    """
    return(error_message)

def value_error(varname, inp,  exp, res):
    error_message="The function " + varname +" returns the wrong value(s)\n\
    When executed with the input(s), "+ str(inp) +", we expected the\n\
    output, " + str(exp)+", but instead we got " + str(res)
    return(error_message)

def return_error(varname):
    error_message="The function " + varname +" does not return a value"+"""
    Ensure that the function uses the correct syntax for a return statement.  i.e.
        def function_name(input):
            ...
            return (answer)
    """
    return(error_message)

def call_error(varname,callname):
    error_message="The function " + varname +" does not call the function "  + callname+"""
    Make sure that rather than repeating lines of code, your function passes
    input to the previously defined function, e.g.

        def previous_function(input):
            ...
            return (answer)
        def new_function(input):
            ...
            new_answer = some_operation + previous_function(input)
            return(new_answer)
    """
    return(error_message)

def execution_error(varname,inp):
    error_message="The function " + varname +" does not execute correctly \n\
    Test it by adding a function call, e.g.\n\
    \n\
        print("+varname+str(inp)+")\n"
    return(error_message)


def print_error_message(error,varname,inp=(0,), exp=7,result=0,callname='print'):
    from AutoFeedback.bcolors import bcolors

    if (str(error)=="success"):
        print(f"{bcolors.OKGREEN}Function, {varname} is correct!\n{bcolors.ENDC}")

    else:
        if (str(error)=="existence"):
            emsg=existence_error(varname)
        elif (str(error)=="inputs"):
            emsg=input_error(varname,len(inp))
        elif (str(error)=="outputs"):
            if hasattr(exp, "get_error") and callable(exp.get_error) : emsg=exp.get_error("values returned from the function " + varname + " with input parameters " + str(inp))
            else : emsg=value_error(varname,inp,exp,result)
        elif (str(error)=="return"):
            emsg=return_error(varname)
        elif (str(error)=="calls"):
            emsg=call_error(varname,callname)
        elif (str(error)=="execution"):
            emsg=execution_error(varname,inp)
        else:
            emsg=("something not right with "+varname)
        print(f"{bcolors.FAIL}{emsg}{bcolors.ENDC}")
    print(f"{bcolors.WARNING}{30*'='}\n{bcolors.ENDC}")
