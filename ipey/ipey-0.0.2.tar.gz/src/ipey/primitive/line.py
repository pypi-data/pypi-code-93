from ipey.primitive import Primitive

from re import T
import xml.etree.ElementTree as ET


class Line(Primitive):

    def __init__(self, points):
        super().__init__()
        self.points = list(points)

    def addPoint(self, point):
        self.points.append(point)
        return

    def getBB(self):
        maxX = max(self.points, key=lambda item:item[0])[0]
        maxY = max(self.points, key=lambda item:item[1])[1]
        minX = min(self.points, key=lambda item:item[0])[0]
        minY = min(self.points, key=lambda item:item[1])[1]

        return ((minX, minY), (maxX, maxY))

    def draw(self):
        elem = ET.Element('path')
        self.addProperties(elem)

        s = ''
        sT = 'm '

        for (x,y) in self.points:
            s += f'{x + self.xP} {y + self.yP} {sT}'
            sT = 'l '

        elem.text = s
        return elem
