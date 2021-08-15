from os import path
from robot.parsing.model import ResourceFile
from  ntutrun.testDataNode import *
from  ntutrun.Builder import *
class ResourceBuilder(Builder):
    def __init__(self):
        self.root = None

    def find_resource(self, testData, result):
        for lib in testData.imports:
            source = path.normpath(testData.directory+'/'+lib.name)
            if  source.endswith(".py") or source.endswith(".txt"):
                pass
            else:
                source = path.normpath(source+'.py')
            if path.exists(source):
                if source not in result.keys():
                    if source.endswith(".py"):
                        continue
                    resource = ResourceFile(source=source).populate()
                    node = TestDataNode(resource)
                    node.add_child(TestDataNode(testData))
                    result[source] = node
                    self.find_resource(resource,result)
                else:
                    result[source].add_child(TestDataNode(testData))
        for child in testData.children:
            self.find_resource(child, result)

    def build(self,testDataDir):
        result = {}
        self.find_resource(testDataDir,result)
        ResourceFileCommomKeyword=[]
        for i in result:
            ResourceFileCommomKeyword.append(ResourceFile(source=i).populate())
        return ResourceFileCommomKeyword
