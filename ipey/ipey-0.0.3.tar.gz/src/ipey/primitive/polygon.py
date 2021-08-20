from ipey.primitive.line import Line

import xml.etree.ElementTree as ET



class Polygon(Line):
    def __init__(self, points, prototype=None):
        super().__init__(points, prototype=prototype)

    def draw(self):
        elem = ET.Element('path')
        self.addProperties(elem)

        s = ''
        sT = 'm '

        for (x,y) in self.points:
            s += f'{x + self.xP} {y + self.yP} {sT}'
            sT = 'l '

        s += ' h'    
        elem.text = s
        return elem
