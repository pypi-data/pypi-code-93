from ipey.primitive import Line

import xml.etree.ElementTree as ET



class Splinegon(Line):
    def __init__(self, points, prototype=None):
        super().__init__(points, prototype)

    def draw(self):
        elem = ET.Element('path', attrib={'layer': self.layer})
        self.addProperties(elem)

        s = ''

        for (x,y) in self.points:
            s += f'{x + self.xP} {y + self.yP}'

        s += ' u'    
        elem.text = s
        return elem