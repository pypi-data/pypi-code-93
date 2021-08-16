'''
Created on 24 mei 2018

@author: ex03210
'''

#import files
import unittest

from nemonet.engines.graph import Graph, Vertex


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

        self.tree.addVertex(a)
        self.tree.addVertex(b)
        self.tree.addVertex(c)
        self.tree.addVertex(d)
        self.tree.addVertex(e)
        self.tree.addVertex(f)

        self.assertTrue(a.nbrOfEdges() == 0)
        self.assertTrue(b.nbrOfEdges() == 0)
        self.assertTrue(c.nbrOfEdges() == 0)
        self.assertTrue(d.nbrOfEdges() == 0)
        self.assertTrue(e.nbrOfEdges() == 0)
        self.assertTrue(f.nbrOfEdges() == 0)

        self.tree.addEdge( a, b )
        self.tree.addEdge( a, c )
        self.tree.addEdge( b, d )
        self.tree.addEdge( b, e )
        self.tree.addEdge( d, f )

        self.assertTrue(a.nbrOfEdges() == 2)
        self.assertTrue(b.nbrOfEdges() == 2)
        self.assertTrue(c.nbrOfEdges() == 0)
        self.assertTrue(d.nbrOfEdges() == 1)
        self.assertTrue(e.nbrOfEdges() == 0)
        self.assertTrue(f.nbrOfEdges() == 0)





    def test_leaf(self):
        l = self.tree.verticesWithNoEdges()
        self.assertTrue(len( l ) == 3 )
        names = [x.name for x in l]
        self.assertTrue( 'C' in names )
        self.assertTrue( 'E' in names )
        self.assertTrue( 'F' in names )

    def test_degree(self):
        # it is possible to figure out what the root node is,
        # it is the node (or vertex) with only outgoing edges
        v = self.tree.getVertex('A')
        self.assertTrue( self.tree.isStart(v) )
        self.assertFalse( self.tree.isEnd(v) )

        v = self.tree.getVertex('B')
        self.assertFalse( self.tree.isStart(v) )
        self.assertFalse( self.tree.isEnd(v) )

        vc = self.tree.getVertex('C')
        ve = self.tree.getVertex('E')
        vf = self.tree.getVertex('F')
        self.assertFalse(self.tree.isStart( vc ) )
        self.assertFalse(self.tree.isStart( ve ) )
        self.assertFalse(self.tree.isStart( vf ) )

        self.assertTrue(self.tree.isEnd( vc ) )
        self.assertTrue(self.tree.isEnd( ve ) )
        self.assertTrue(self.tree.isEnd( vf ) )

    def test_startEndPointPaths(self):
        #get a list of vertices and check if it is a start point
        #get a list of vertices and check if it is an end point
        #check if a path exist between al begin and end points
        startPoints = []
        endPoints = []
        nameList = self.tree.getAllNames()

        for name in nameList:
            v = self.tree.getVertex( name )
            if self.tree.isStart( v ):
                startPoints.append( v )
            if self.tree.isEnd( v ):
                endPoints.append( v )

        self.assertTrue( len( startPoints ) == 1 )
        self.assertTrue( len( endPoints ) == 3 )

        paths = []

        for start in startPoints:
            for end in endPoints:
                paths.append( self.tree.find_path(start.name, end.name ) )

        self.assertTrue( ['A', 'C'] in paths )
        self.assertTrue( ['A', 'B', 'E'] in paths )
        self.assertTrue( ['A', 'B', 'D', 'F'] in paths )


    def test_path(self):
        self.assertTrue( ['A', 'B', 'D', 'F'] == self.tree.find_path( 'A', 'F' ) )
        self.assertTrue( [ 'A', 'B', 'E'] == self.tree.find_path('A', 'E'))

    def tearDown(self):
        self.tree = None


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()