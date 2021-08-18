from abc import abstractmethod
import xml.etree.ElementTree as ET
import copy

class Primitive:
    xP = 0
    yP = 0

    def __init__(self):
        self.fill = None
        self.stroke = 'black'
        self.pen = 'normal'
        # self.MR = [[1, 0], [0,1]]
        # self.MT = [0, 0]

    def cloneProp(self, other):
        self.fill = other.fill
        self.stroke = other.stroke
        self.pen = other.pen

    def addProperties(self, elem):
        elem.set('pen', self.pen)
        
        if self.fill:
            elem.set('fill', self.fill)

        if self.stroke:
            elem.set('stroke', self.stroke)

    def copy(self):
        return copy.deepcopy(self)
        # elem.set('matrix', f'{self.MR[0][0]} {self.MR[0][1]} {self.MR[1][0]} {self.MR[1][1]} {self.MT[0]} {self.MT[1]}')

    @abstractmethod
    def getBB(self):
        raise NotImplemented

    @abstractmethod
    def translate(self, x, y):
        raise NotImplemented

    @abstractmethod
    def rotate(self, a):
        raise NotImplemented

    @abstractmethod
    def draw() -> ET.Element:
        raise NotImplemented


