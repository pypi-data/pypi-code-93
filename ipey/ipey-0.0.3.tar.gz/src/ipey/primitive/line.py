from ipey.primitive import Primitive

from re import T
import xml.etree.ElementTree as ET
import math

class Line(Primitive):

    def __init__(self, points, prototype = None):
        super().__init__(prototype=prototype)

        if len(points) < 2:
            raise Exception

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


    def translate(self, x, y):
        for i, p in enumerate(self.points):
            self.points[i] = (p[0] + x, p[1] + y)


    def rotate(self, a, pivot=None):
        if pivot:
            xP, yP = pivot
        else:
            xP = 0
            yP = 0
            for p in self.points:
                xP += p[0]
                yP += p[1]
                
            yP /= len(self.points)
            xP /= len(self.points)


        s = math.sin(a)
        c = math.cos(a)
        for i, p in enumerate(self.points):
            p = (p[0] - xP, p[1] - yP)
            p = (p[0] * c + p[1] * s, p[0] * s + p[1] * c)
            self.points[i] = (p[0] + xP, p[1] + yP)

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
