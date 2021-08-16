"""
常用高阶函数迭代器库。
"""
from types import FunctionType
from typing import Iterable
    
import sys



class XIterator:
    """迭代器基类。封装了collection的基本操作。

    - 该类满足迭代器协议。封装了__iter__和__next__
    """

    def repeat(self, n:int=-1):
        return repeat(self, n) 

    def apply( self, action, *args, **kargs ):
        return action( *args, self, **kargs )
       
    def filter( self, criteria ):
        return filter( criteria, self )

    def map( self, action ):
        return map( action, self )

    def reduce( self, action, init=None ):
        return reduce( action, self, init=init )

    def partition( self, size ):
        return partition( self, size )

  #def flatten(self, level=1):
  #      return xflatten( self, level=level )
        
    def to_list(self): return list(self)

    def __iter__(self): return self

    def __next__(self): return self

    def foreach( self, action ):
        for e in self:
            action(e)
        return self


# class iter(XIterator):
#     def __init__(self, ite):
#         self.ite = ite

#     def __iter__(self):
#         return iter(self.ite)


class partition(XIterator):

    def __init__(self, ite, size=1):
        self.ite = ite
        self.size = size

    def __iter__(self):
        self._nxt_ = iter(self)
        return self

    def __next__(self):
        rst = []
        try:
            for _ in range(self.size):
                v = next(self._nxt_)
                rst.append(v)
        except StopIteration:
            if len(rst) == 0:
                raise StopIteration()

        return rst                


class range(XIterator):

    def __init__(self, *pos):
        ipos = [0] if len(pos)==0 else pos
        self.posGrp = partition( ipos, 4 ).to_list()

        self.begin = 0
        self.end = 0
        self.step = 0
        self.repeat = 0
        self.grpPtr = -1
        self.rptPtr = 0
        self.value = 0

        self.reload()

    def reload( self, upGrp=True ):
        if upGrp:
            self.grpPtr = self.grpPtr + 1
            self.rptPtr = 0
        else:
            self.rptPtr = self.rptPtr + 1

        if self.grpPtr < len(self.posGrp):
            grp = self.posGrp[self.grpPtr]
            self.begin  = grp[0] if len(grp) >= 1 else 0
            self.end    = grp[1] if len(grp) >= 2 else self.begin-1
            self.step   = grp[2] if len(grp) >= 3 else 1
            self.repeat = grp[3] if len(grp) >= 4 else 1
            
        self.value = self.begin

    def __next__(self):

        if self.grpPtr>=len(self.posGrp):
            raise StopIteration()

        ret = self.value
        self.value = self.value + self.step

        if (self.begin <= self.end and self.value >= self.end) or (self.begin >= self.end and self.value <= self.end): 
            self.reload( self.rptPtr+1 >= self.repeat and self.repeat > 0 )

        return ret


class repeat(XIterator):
    """repeat迭代器

    Argument:
    * ite: {iterator} ---- 可迭代对象
    * n: {int} ---- ite迭代次数
      * -1：无限循环
      * other: 循环次数
    """

    def __init__(self, ite, n=-1):
        self.ite = ite
        self.n = None
        self._nxt_ = None
        self._nun_ = n

    def __iter__(self):
        self._nxt_ = None
        self._num_ = 0
        return self

    def __next__(self):

        if self._num_ >= self.n and self.n > 0 :
            raise StopIteration()

        if self._nxt_ == None:
            self._num_ = self._num_ + 1 
            self._nxt_ = iter(self.ite)

        nxt = next(self._nxt_) 
        self._num_ = self._num_ + 1

        return nxt



class map(XIterator):
    def __init__(self, action, ite):
        """
        返回一个xmap迭代器。

        Argument:
        * action: {Action} -- 对每个元素的处理函数。
          * Action格式定义参见'high order function.html'
          * 每个action函数的格式为: 
            * proc(ele) -> value
            * proc(ele, **args) -> value
            * proc(*eles, **args) -> value
        * iters: {iterable} -- 被处理的数据迭代器。
          * 当该迭代器为空时，返回一个支持proc的延时函数，该函数接收一个列表参数。(Delay Execute特性)
        * criteria: {None(default) | list} -- 分组条件
          * 参见'high order function.html'
        * others: -- proc处理所需的参数列表
            
        Returns:
        Iterator -- 处理结果迭代器。
        * 返回的是迭代器，需要使用list(return-value)来转化为链表。
        * next迭代返回一个列表结果；当列表中仅包含一个元素时，返回该元素
        """
        self.action = action
        self.ite = ite

    def __iter__(self):
        self._nxt_ = iter(self.ite) 
        return self

    def __next__(self):

        nxt = next(self._nxt_) 

        rst = self.action( nxt )
        return rst
        
    def __call__( self, ite ):
        self.ite = ite
        return self



class filter(XIterator):
    def __init__(self, criteria, iters ):
        self.criteria = criteria
        self.iters = iters

    def __iter__(self):
        self._nxt_ = iter(self.iters)
        return self

    def __next__(self):

        nxt = next( self._nxt_ ) 

        rst = self.criteria( nxt )
        if rst == False: 
            return self.__next__()
            
        return nxt
        
    def __call__( self, *iters, **kargs ):
        self.iters = iters
        return self



class accumulate(XIterator):
    """累积计算

    相当于：[reduce(ite[0]), reduce(ite[0:1]), reduce(ite[0:2]), reduce(ite[0:3]), ...]
    """

    def __init__(self, action, ite:Iterable):
        self.action = action
        self.ite = ite
        self.acc = None

    def __iter__(self):
        self._nxt_ = iter(self.ite)
        self.acc = None
        return self

    def __next__(self):

        if self.acc == None:
            return next(self._nxt_)

        return self.action(self.acc, next(self._nxt_)) 



def reduce( action, ite:Iterable, init=None ):
    # 初始化变量
    nxt = iter(ite)
   
    try:
        if init == None:
            last = next(nxt) 
        else:
            last = init

        while True:
            curr = next(nxt) 
            last = action(last, curr)

    except StopIteration:
        pass

    return last





def apply( actions, args=None, **kargs ):
    """
    高阶函数降级处理。
    Constraint-001: 当actions仅包含一个元素时，该action必须满足格式：(*args, **kargs)
    Constraint-002: 当actions包含多个元素时，非最后一个action元素必须满足格式：(action, *args, **kargs)
    """
    if args == None:
        def _action_( *args1 ):
            return apply( actions, args1, **kargs )
        return _action_
    
    if not isinstance( actions, (tuple, list) ):
        actions = [actions]
    
    action_num = len( actions )

    # 0阶处理：直接返回数据
    if action_num == 0: return args
        
    # 1阶处理：返回处理的结果
    # Issue: 该1阶处理函数是否有该调用格式？这里貌似多了一个协议接口定义
    if action_num == 1: return actions[0]( *args, **kargs )

    # 2阶函数，直接求解该2阶函数的解
    if action_num == 2: return actions[0]( actions[1], *args, **kargs )

    # 高于2阶函数，逐阶降阶处理
    def _sub_(*s, **kargs): return apply(actions[1:], s, **kargs)
    return actions[0]( _sub_, *args, **kargs )

def xapply( actions, *args, **kargs ):
    return apply( actions, args, **kargs )
    
def wapply( *args, **kargs ):
    if 'anum' in kargs:
        action_num = kargs.get( 'anum', 0 )
        del kargs['anum']
    else:
        action_num = 0
    
    if action_num == 0:
        for i in range( len(args) ):
            if not hasattr( args[i], '__call__' ):
                break
        actions = args[:i]
        args = args[i:]
    else:
        actions = args[:action_num]
        args = args[action_num:]
        
    return apply( actions, args, **kargs )



##############################################################################################
##  cross
##############################################################################################
class cross(XIterator):

    def __init__(self, *ites):
        self.ites = ites

    def __iter__(self):
        return self 

    def __next__(self):

        def inner_cross(*ites):
            if len(ites)==1:
                for ite in ites:
                    yield [ite]
            else:
                for ite in ites[0]:
                    yield [ite].concat( *ites[1:] )

        return tuple(inner_cross(*self.ites))

    
