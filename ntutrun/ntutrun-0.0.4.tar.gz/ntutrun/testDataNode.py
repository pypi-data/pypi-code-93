class TestDataNode:
    def __init__(self, testData):
        self.test_data = testData
        self.childs = []

    def set_parent(self,parent):
        self.parent = parent

    def remove_child(self, child):
        child.set_parent(None)        
        self.childs.remove(child)

    def add_child(self, child):
        self.childs.append(child)
        child.set_parent(self)
    
    def accept(self, visitor):
        visitor.visit(self)