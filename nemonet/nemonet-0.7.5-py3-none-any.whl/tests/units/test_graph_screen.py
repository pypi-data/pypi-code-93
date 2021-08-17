import unittest

from bs4 import BeautifulSoup

from nemonet.engines.graph import Vertex, Graph, Action

#tests
class Test(unittest.TestCase):

    def setUp(self):
        self.tree = Graph()
        a = Vertex('A')
        b = Vertex('B')
        c = Vertex('C')
        d = Vertex('D')
        e = Vertex('E')
        f = Vertex('F')
        g = Vertex('G')
        h = Vertex('H')
        i = Vertex('I')
        j = Vertex('J')

        self.tree.addVertex(a)
        self.tree.addVertex(b)
        self.tree.addVertex(c)
        self.tree.addVertex(d)
        self.tree.addVertex(e)
        self.tree.addVertex(f)
        self.tree.addVertex(g)
        self.tree.addVertex(h)
        self.tree.addVertex(i)
        self.tree.addVertex(j)

        self.tree.addEdge(a, c)
        self.tree.addEdge(a, d)

        self.tree.addEdge(b, f)
        self.tree.addEdge(b, g)
        self.tree.addEdge(b, h)

        self.tree.addEdge(c, e)

        self.tree.addEdge(d, f)
        self.tree.addEdge(d, g)
        self.tree.addEdge(d, h)

        self.tree.addEdge(e, f)
        self.tree.addEdge(e, h)
        self.tree.addEdge(e, g)

        self.tree.addEdge(f, i)

        self.tree.addEdge(g, j)

    def tearDown(self):
        self.tree = None

    def test_edges(self):
        l = self.tree.verticesWithNoEdges()
        self.assertTrue( len( l ) == 3 )
        leafes = [x.name for x in l]
        self.assertTrue( ['H', 'I', 'J'] == leafes )

    def test_start_end_points(self):
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
        self.assertTrue( enders == ['H', 'I', 'J'] )


    def test_all_paths(self):
        pa = self.tree.find_all_paths('A', 'I')
        self.assertTrue( pa == [['A', 'C', 'E', 'F', 'I'], ['A', 'D', 'F', 'I']] )
        pa = self.tree.find_all_paths('A', 'J')
        self.assertTrue( pa == [['A', 'C', 'E', 'G', 'J'], ['A', 'D', 'G', 'J']] )
        pa = self.tree.find_all_paths('A', 'H')
        self.assertTrue( pa == [['A', 'C', 'E', 'H'], ['A', 'D', 'H']] )

        pa = self.tree.find_all_paths('B', 'I')
        self.assertTrue( pa == [['B', 'F', 'I']] )

        pa = self.tree.find_all_paths('B', 'J')
        self.assertTrue( pa == [['B', 'G', 'J']] )

        pa = self.tree.find_all_paths('B', 'H')
        self.assertTrue( pa == [['B', 'H']] )

    def test_couple_actions(self):
        aForA = Action( "//label[contains(@for,'isConstructionyes')]", 'CLICKABLE' )
        aForB = Action( "//label[contains(@for,'isConstructionno')]", 'CLICKABLE')
        aForC = Action( "//label[contains(@for,'hasBuildingPermityes')]", 'CLICKABLE')
        aForD = Action( "//label[contains(@for,'hasBuildingPermitno')]", 'CLICKABLE')
        aForE = Action("//input[@id='buildingPermitNumber']", 'TEXTABLE')
        aForF = Action("//label[contains(@for,'EXISTING_PROJECT')]", 'CLICKABLE')
        aForG = Action("//label[contains(@for,'NEW_PROJECT')]", 'CLICKABLE')
        aForH = Action("//label[contains(@for,'NO')]", 'CLICKABLE')
        aForI = Action("//select[@id='projectSelect']/option[contains(@value,'Project 2')]", 'CLICKABLE')
        aForJ = Action("//input[@id='projectName']", 'TEXTABLE')

        va = self.tree.getVertex('A')
        vb = self.tree.getVertex('B')
        vc = self.tree.getVertex('C')
        vd = self.tree.getVertex('D')
        ve = self.tree.getVertex('E')
        vf = self.tree.getVertex('F')
        vg = self.tree.getVertex('G')
        vh = self.tree.getVertex('H')
        vi = self.tree.getVertex('I')
        vj = self.tree.getVertex('J')

        va.addAction(aForA)
        vb.addAction(aForB)
        vc.addAction(aForC)
        vd.addAction(aForD)
        ve.addAction(aForE)
        vf.addAction(aForF)
        vg.addAction(aForG)
        vh.addAction(aForH)
        vi.addAction(aForI)
        vj.addAction(aForJ)

        nameList = self.tree.getAllNames()

        # check if the calls on action exists
        for name in nameList:
            a = self.tree.getVertex(name).getAction()
            a.getXpathStr()
            a.getElementType()

    def test_with_graph_file(self):
        with open("graph-screen-type.xml") as fp:
            soup = BeautifulSoup(fp, "lxml")
        for node in soup.find_all('node'):
            print( node['name'] )

        for edge in soup.find_all('edge'):
            print( "from =%s to=%s" % (edge['from'] ,edge['to'] ) )

        for action in soup.find_all('action'):
            print(action['xpath'])
            print(action['type'])
            print(action['nodename'])