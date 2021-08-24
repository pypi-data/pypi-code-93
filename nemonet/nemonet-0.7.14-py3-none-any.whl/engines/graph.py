from bs4 import BeautifulSoup
from graphviz import Digraph

class Step(object):
    def __init__(self, nbr, nodename, action):
        self.nbr = nbr
        self.nodename = nodename
        self.action = action

    def getNbr(self):
        return self.nbr

    def getNodename(self):
        return self.nodename

    def getAction(self):
        return self.action

class Action(object):

    def __init__( self, xpathStr, elementType, value=None, wait_after=0, key=None):
        self.xpathStr = xpathStr
        self.et = elementType
        self.value = value
        self.wait_after = int( wait_after )
        self.key = key

    def getXpathStr(self):
        return self.xpathStr

    def getElementType(self):
        return self.et

    def getValue(self):
        return self.value

    def get_wait_after(self):
        return self.wait_after

    def set_wait_after(self, wait_after=0):
        self.wait_after = int( wait_after )

    def set_key(self, key):
        self.key = key

    def get_key(self):
        return self.key


class Vertex( object ):
    def __init__( self, name ):
        self.name = name
        self.edges = []
        self.degreeOut = 0
        self.degreeIn = 0
        self.action = None

    def addEdge( self, vertex ):
        if len( list(filter(lambda v: v.name == vertex.name , self.edges ) ) ) == 0:
            self.edges.append( vertex )

    def nbrOfEdges(self):
        return len( self.edges )

    def incDegreeOut(self):
        self.degreeOut += 1

    def incDegreeIn(self):
        self.degreeIn += 1

    def addAction( self, action ):
        self.action = action

    def getAction(self):
        return self.action

class Graph( object ):
    def __init__(self):
        self.structure = {}
        self.incoming = []
        self.outgoing = []
        self.setup = []
        self.actions = {}

    def addVertex( self, vertex):
        if not vertex.name in self.structure.keys():
            self.structure[ vertex.name ] = vertex

    def find_path( self, start, end, path=[]):
        path = path + [start]
        if start == end:
            return path
        if not start in self.structure.keys():
            return None
        for node in self.structure[start].edges:
            if node.name not in path:
                newpath = self.find_path( node.name, end, path)
                if newpath: return newpath
        return None

    def find_all_paths(self, start, end, path=[]):
        path = path + [start]
        if start == end:
            return [path]
        if not start in self.structure.keys():
            return []
        paths = []
        for node in self.structure[start].edges:
            if node.name not in path:
                newpaths = self.find_all_paths( node.name, end, path)
                for newpath in newpaths:
                    paths.append(newpath)
        return paths

    def vertices(self):
        return self.structure.values()

    def verticesWithNoEdges(self):
        v = self.vertices()
        noEdge = []
        for item in v:
            if item.nbrOfEdges() == 0:
                noEdge.append( item )
        return noEdge

    def __addIncoming__( self, vertex ):
        if len(list(filter(lambda v: v.name == vertex.name, self.incoming))) == 0:
            self.incoming.append(vertex)

    def __addOutgoing__( self, vertex ):
        if len(list(filter(lambda v: v.name == vertex.name, self.outgoing))) == 0:
            self.outgoing.append(vertex)

    def addEdge( self, start, end ):
        start.addEdge( end )
        self.__addOutgoing__( start )
        start.incDegreeOut()
        self.__addIncoming__( end )
        end.incDegreeIn()

    def hasIncoming(self, vertex):
        if len(list(filter(lambda v: v.name == vertex.name, self.incoming))) == 0:
            return False
        else:
            return True

    def hasOutGoing(self, vertex):
        if len(list(filter(lambda v: v.name == vertex.name, self.outgoing))) == 0:
            return False
        else:
            return True

    def isStart( self, vertex ):
        if not self.hasIncoming(vertex) and self.hasOutGoing(vertex):
            return True
        else:
            return False

    def isEnd( self, vertex ):
        if self.hasIncoming(vertex) and not self.hasOutGoing(vertex):
            return True
        else:
            return False

    def getVertex(self , name ):
        return self.structure[ name ]

    def getAllNames(self):
        return self.structure.keys()

    def getSetup(self):
        return self.setup

    def build(self , fileName ):
        dig = Digraph(comment=fileName)
        with open( fileName + ".xml") as fp:
            soup = BeautifulSoup(fp, "lxml")
        for node in soup.find_all('node'):
            v = Vertex(node['name'])
            self.addVertex(v)
            dig.node(node['name'])

        for edge in soup.find_all('edge'):
            fromV = self.getVertex(edge['from'])
            toV = self.getVertex(edge['to'])
            self.addEdge(fromV, toV)
            dig.edge(fromV.name, toV.name)
        for action in soup.find_all('action'):
            if 'value' in action.attrs:
                a = Action(action['xpath'], action['type'], action['value'] )
            else:
                a = Action(action['xpath'], action['type'])
            if 'waitafter' in action.attrs:
                a.set_wait_after( action['waitafter'] )
            if 'key' in action.attrs:
                a.set_key( action['key'] )
            v = self.getVertex(action['nodename'])
            v.addAction(a)
            self.actions[action['nodename']] = a

        for step in soup.find_all('step'):
            self.setup.append(Step(step['nbr'], step['nodename'], self.actions[step['nodename']] ) )

        self.setup.sort(key=lambda x: x.nbr, reverse=False)

        dig.render( fileName + ".gv" )