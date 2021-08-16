
def recur(arr, ofst, result, createNode, level, currLvl):
    """
    # Arguments:
    * result: {List} ---- 父元素的children节点ListBuffer
    * return: 下一个遍历数组指针
    * currLvl: {Int} ---- 当前处理的节点在树种的层次(level)。对于单根树，root节点的currLvl=0; 对于多根树,各个root节点的currLvl=1

    # 算法思路：
    * 依次循环arr数组中的元素
      * 若当前元素和下一个元素的level相等（判断为：当前节点和下一个节点是brother关系），则
        * 父元素的children加入当前元素，arr指针加1
        * 继续循环
      * 若当前元素的level大于下一个元素（判断为：当前节点和下一个节点是侄子-叔祖辈关系），则
        * 构造当前节点，并入父节点的children列表
        * 返回迭代，指针移到下一个节点
      * 若当前元素的level小于下一个元素（判断为：当前节点和下一个节点是parent-child关系），则
        * 以当前节点为主节点，进行迭代
    """

    while ofst < len(arr)-1:  # 至少还有2个元素

        e = arr[ofst]   # 获取迭代元素
        lvl = level(e)  # 获取元素层级关系
        nxt_lvl = level(arr[ofst+1])
                
        if lvl < currLvl: # 侄辈返回到叔祖辈过程中，若还没有返回到叔祖辈的层级，则继续返回
            return ofst     # 继续返回，意思就是arr指针维持不变。退出到下一层的迭代

        elif lvl == nxt_lvl:   # 当前元素是一个leaf节点，下一个节点和当前节点是兄弟
            ele = createNode( e, [] )   # 叶子节点，无子节点
            result.append(ele)      # 父节点加入当前节点
            ofst = ofst + 1

        elif lvl > nxt_lvl:  # 当前元素是一个leaf节点，下一个元素是当前元素的叔祖辈
            ele = createNode( e, [] )   # 叶子节点，无子节点
            result.append(ele)      # 父节点加入当前节点
            return ofst+1

        else: # 当前元素还有子元素
            sub_result = []     # 子元素集合：由子元素迭代时隙填充
            ofst = recur( arr, ofst+1, sub_result, createNode, level, currLvl+1 )    # 子元素迭代
            ele = createNode( e, sub_result )   # 子填充完sub_result后，创建元素
            result.append(ele)  # 填充父元素的result

    # 最后一个元素处理：必定是一个叶子节点
    if ofst == len(arr)-1:
        ele = createNode( arr[ofst], [] )
        result.append(ele)
        ofst = ofst + 1

    return ofst


def map_iter(node, idx, stack, wide, children, actionb, actionl):
    childs = children(node)
    sstack = stack + [node]
    if childs:
        ret = []
        for i in range(len(childs)):
            ret.append(map_iter( childs[i], idx+[i], sstack, wide+[len(childs)], children, actionb, actionl ))
        return actionb( node, idx, ret, sstack, wide )
    else:
        return actionl( node, idx, [], sstack, wide )


class XTree:

    def __init__(self, node, children=None):
        """树结构操作类

        **Arguments**
        * node:
        * hasRoot:
        * children:
        """
        self.node = node

        if children == None:
            if hasattr(node, "children"):
                self.children = lambda x : x.children
            else:
                raise Exception("Invalid children is set!")
        else:   ## 更严格来说，应该要判断是否是可调用函数
            self.children = children

    @staticmethod
    def fromArray( arr, children, createNode, level ):
        """从一个元素列表构建树/多树
        **Arguments**
        * arr: List[T] ---- 元素列表
        * createNode: (e:T,child:List[Node]|None=None)=>Node ---- 构建树节点函数
          * e: 元素列表中每个元素
          * child: 子元素列表。fromArray构建的子节点列表
          * Return: 树节点
        * children: (n:Node)=>List[Node] ---- 如何从树节点获取其子节点的列表函数
          * n: 当前节点
          * Return: 返回的子节点列表
        * level: (e:T)=>Int ---- 如何获取元素在树中的层次函数
          * e: 元素
          * Return: 在树中的层次
        * Return: 构建的新的XTree树结构
        """
        result = []
        recur( arr, 0, result, createNode, level )
        return XTree(result[0], children)

    def map( self, actionb, actionl=None ):
        if actionl==None: actionl = actionb

        return map_iter( self.node, [], [], [], self.children, actionb, actionl )


class MTree:
    def __init__(self, nodes, children=None):
        self.nodes = nodes

        if children == None:
            self.children = lambda x : x.children
        else:   ## 更严格来说，应该要判断是否是可调用函数
            self.children = children

    @staticmethod
    def fromArray( arr, createNode, level ):
        """从数组构建多树
        # Arguments:
        * arr: {Array[T]} ---- 节点数组
        * children: {Function[T,List[T]]} ---- 节点获取子节点函数
        * createNode: {Function[]}  ---- 节点构造函数
        * level: {Function[]} ---- 获取树节点来的
        """
        result = []
        recur( arr, 0, result, createNode, level, 1 )
        return result

    def map( self, actionb, actionl=None ):
        if actionl==None: actionl = actionb

        res = []
        for i in range(len(self.nodes)):
            res.append(map_iter(
                    self.nodes[i], [i], 
                    [self.nodes], [len(self.nodes)],
                    self.children, actionb, actionl
                ))
        return res

