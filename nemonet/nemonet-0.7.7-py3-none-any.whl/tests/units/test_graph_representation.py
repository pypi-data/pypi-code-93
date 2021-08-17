import unittest

from bs4 import BeautifulSoup

from graphviz import Digraph

from nemonet.engines.graph import Graph, Vertex, Action

class MyTestCase(unittest.TestCase):

    def setUp(self):
        self.tree = Graph()
        self.buildGrapFromFile()

    def tearDown(self):
        self.tree = None

    def test_cases(self):
        startPoints = []
        endPoints = []
        nameList = self.tree.getAllNames()

        for name in nameList:
            v = self.tree.getVertex(name)
            if self.tree.isStart(v):
                startPoints.append(v)
            if self.tree.isEnd(v):
                endPoints.append(v)

        self.assertTrue(len(startPoints) == 2)
        self.assertTrue(len(endPoints) == 3)

        starters = [x.name for x in startPoints]
        enders = [x.name for x in endPoints]

        self.assertTrue( starters == ['A', 'B'] )
        self.assertTrue( enders == ['G', 'H', 'I'] )

        allThePaths = []

        for s in starters:
            for e in enders:
                pa = self.tree.find_all_paths(s, e)
                allThePaths = allThePaths + pa

        self.assertTrue( ['A', 'C', 'E', 'F', 'I'] in allThePaths )
        self.assertTrue( ['A', 'C', 'E', 'H'] in allThePaths )
        self.assertTrue( ['A', 'C', 'E', 'G'] in allThePaths )
        self.assertTrue( ['A', 'D', 'F', 'I'] in allThePaths )
        self.assertTrue( ['A', 'D', 'G'] in allThePaths )
        self.assertTrue( ['A', 'D', 'H'] in allThePaths )
        self.assertTrue( ['B', 'F', 'I'] in allThePaths )
        self.assertTrue( ['B', 'G'] in allThePaths )
        self.assertTrue( ['B', 'H'] in allThePaths )


    def buildGrapFromFile(self):
        dig = Digraph(comment='Type Screen')
        with open("graph-screen-type.xml") as fp:
            soup = BeautifulSoup(fp, "lxml")
        for node in soup.find_all('node'):
            v = Vertex(node['name'])
            self.tree.addVertex(v)
            dig.node(node['name'])

        for edge in soup.find_all('edge'):
            fromV = self.tree.getVertex(edge['from'])
            toV = self.tree.getVertex(edge['to'])
            self.tree.addEdge(fromV, toV)
            dig.edge(fromV.name,toV.name)
        for action in soup.find_all('action'):
            a = Action(action['xpath'], action['type'])
            v = self.tree.getVertex(action['nodename'])
            v.addAction(a)

        dig.render('testtypescreen')

if __name__ == '__main__':
    unittest.main()
