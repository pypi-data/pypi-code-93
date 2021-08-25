from graphviz import Digraph
from DSViz.NoneError import NoneError

class BinaryTreeV:
    def __init__(self):
        self.dot = Digraph()
            
    def add(self, parent, left = None, right = None):
        if parent is None:
            raise NoneError("Parent node cannot be None")
        self.dot.node(str(parent),str(parent))
        if left is not None:        
            self.dot.edge(str(parent), str(left))
        else:
            self.dot.node(name = str(parent)+'invisl', lable = str(parent)+'invisl', style = 'invis')
            self.dot.edge(str(parent), str(parent)+'invisl')
        if right is not None:
            self.dot.edge(str(parent), str(right))
        else:
            self.dot.node(name = str(parent)+'invisl', lable = str(parent)+'invisl', style = 'invis')
            self.dot.edge(str(parent), str(parent)+'invisl')

        
    @property
    def show(self):
        self.dot.render('DSViz/test-output/graph.gv', view=True)

