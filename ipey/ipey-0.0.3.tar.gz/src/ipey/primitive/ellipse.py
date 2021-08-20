from ipey.primitive.primitive import Primitive
import xml.etree.ElementTree as ET

class Ellipse(Primitive):
    def __init__(self, c, v, cov, prototype = None):
        super().__init__(prototype=prototype)
        self.center = c
        self.vertex = v
        self.co_vertex = cov

    def getBB(self):
        raise NotImplementedError

    def draw(self):
        elem = ET.Element('path')
        self.addProperties(elem)
        elem.text = f'{self.vertex[0]} {self.vertex[0]} {self.co_vertex[1]} {self.co_vertex[1]} {self.center[0]} {self.center[1]} e'
        return elem