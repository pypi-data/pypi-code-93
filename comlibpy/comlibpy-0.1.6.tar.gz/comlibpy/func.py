



class Action:
    pass

class bypass(Action):
    """返回一个接收一个参数的bypass函数，无论参数是多少，总是返回`v`"""
    def __init__(self, v):
        self.v = v

    def __call__(self, e):
        return self.v


class partial(Action):
    
    def __init__( self, op, *args, **kargs ):
        self.op = op
        self.args = args
        self.kargs = kargs

    def execute( self, *args, **kargs ):
        return self.op( *args, **kargs )

    def __call__( self, *args, **kargs ):
        args_loc = self.args + args
        kargs_loc = { **self.kargs, **kargs }
        return self.execute( *args_loc, **kargs_loc )




class vparam(Action):
    """返回一个可以支持可变参数的函数。函数格式为：`(a:T, b:optional[T]=None, *cs:T, **kwargs)=>T`。
    该函数其实就是接收2个输入参数的`op`函数的可变参数扩展版本。注意：若仅输入一个参数，则直接返回该参数。"""

    def __init__( self, op ):
        self.op = op

    def param0( self, a ):
        return a

    def __call__(self, a, b=None, *cs, **kwargs):

        if isinstance( a, list ):
            ret = a[0]
            for c in a[1:]:
                ret = self.op( ret, c, **kwargs )
        else:
            ret = self.param0(a)

        if b != None:
            ret = self.op( ret, b, **kwargs )    
        
        for c in cs:
            ret = self.op( ret, c, **kwargs )

        return ret


class vparam1(vparam):
    def param0(self, a):
        return self.op(a)

