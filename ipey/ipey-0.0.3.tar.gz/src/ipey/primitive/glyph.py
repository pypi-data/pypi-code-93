
from ipey.primitive import Primitive

import xml.etree.ElementTree as ET
from enum import Enum
import sys


class Glyph(Primitive):
    def __init__(self, point, type, prototype=None):
        super().__init__(prototype=prototype)

        self.x = point[0]
        self.y = point[1]
        self.type = type
        self.size = "normal" 

    def draw(self):
        elem = ET.Element('use')
        self.addProperties(elem)

        elem.set('size', self.size)
        elem.set('name', self.type)
        elem.set('pos', f'{self.x + self.xP} {self.y + self.yP}')

        return elem

    def getBB(self):
        return ((self.x, self.y), (self.x, self.y))
