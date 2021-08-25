import threading

def thread(func, args):
    '''
    Must be a function in without ()
    example if the function is def hello():
    thread would be called like so thread(func=hello, args=['argument1', 'argument2']
    '''
    Obj = threading.Thread(target=func, args=args)
    Obj.start()
    return Obj

def multiple_threads(function_data):
    """
    Functions must be in a list like so [function1, function2, function3]
    :param function_data:

    List of Dictionary like so
    function_data = [
        {
        'function' : function
        'args' : [arg1, arg2]
        }
    ]

    :return:
    A list of all the started threads
    """
    x = 0
    Objs = []
    for f in function_data:
        Args = f['args']
        if Args == None:
            Args = [None]

        Function = f['function']
        Objs.append(threading.Thread(target=Function, args=Args))


    for o in Objs:
        o.start()


    return Objs

