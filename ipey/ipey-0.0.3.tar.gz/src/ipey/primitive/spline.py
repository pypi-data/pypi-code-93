from ipey.primitive import Primitive

import xml.etree.ElementTree as ET
from enum import Enum


class SplineType(Enum):
    BSPLINE = 0
    CARDINAL = 1
    SPIRO = 2

class Spline(Primitive):
    def __init__(self, points, splineType = SplineType.BSPLINE, prototype = None):
        super().__init__(prototype=prototype)
        self.points = points
        self.splineType = splineType

    def addPoint(self, point):
        self.points.append(point)
        return

    def getBB(self):
        maxX = max(self.points, key=lambda item:item[0])[0]
        maxY = max(self.points, key=lambda item:item[0])[0]
        minX = min(self.points, key=lambda item:item[1])[1]
        minY = min(self.points, key=lambda item:item[1])[1]

        return ((minX, minY), (maxX, maxY))

    def draw(self):
        elem = ET.Element('path')
        self.addProperties(elem)

        s = ''
        sT = 'm '

        for (x,y) in self.points:
            s += f'{x + self.xP} {y + self.yP} {sT}'
            sT = ''

        if self.splineType == SplineType.BSPLINE:
            s += 'c'
        if self.splineType == SplineType.CARDINAL: 
            s += '0.5 C'
        if self.splineType == SplineType.SPIRO: 
            s += '0.5 C'
        
        elem.text = s
        return elem

