import unittest
import random
import string
from nemonet.engines.sequencer import Sequences
from nemonet.engines.graph import Graph

class SequenceTestCase(unittest.TestCase):
    def test_something(self):
        g = Graph()
        g.build('graph-screen-type')
        seq = Sequences(g)
        self.executeSequences(seq, g)

    def click_xpath( self, arg ):
        pass

    def fill_in_text(self, arg, str):
        pass

    def execute_script(self , arg):
        pass

    def click_element_in_list(self, arg, value):
        pass

    def executeSequences(self, seq, g):
        pa = seq.get()
        self.assertTrue( pa == [['A', 'C', 'E', 'G'], ['A', 'D', 'G'], ['A', 'C', 'E', 'H'], ['A', 'D', 'H'], ['A', 'C', 'E', 'F', 'I'], ['A', 'D', 'F', 'I'], ['B', 'G'], ['B', 'H'], ['B', 'F', 'I']])
        for l in pa:
            for el in l:
                a = g.getVertex(el).getAction()

                if a.getElementType() == 'CLICKABLE':
                    self.click_xpath(a.getXpathStr())
                elif a.getElementType() == 'TEXTABLE':
                    rStr = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])
                    self.fill_in_text(a.getXpathStr(), rStr)
                elif a.getElementType() == 'JSexec':
                    self.execute_script(a.getXpathStr())
                elif a.getElementType() == 'SELECTABLE':
                    self.click_element_in_list(a.getXpathStr(), 2)

if __name__ == '__main__':
    unittest.main()
