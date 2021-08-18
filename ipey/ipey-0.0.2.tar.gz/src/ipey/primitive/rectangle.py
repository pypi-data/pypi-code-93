from ipey.primitive import Primitive

import xml.etree.ElementTree as ET



class Rectangle(Primitive):

    def __init__(self, p, w, h, prototype = None):
        super().__init__()
        
        if prototype:
            self.cloneProp(prototype)

        x,y = p
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def getBB(self):
        return ((self.x, self.y - self.h), (self.x + self.w, self.y))

    def translate(self, x, y):
        self.x += x
        self.y += y

    def draw(self):
        elem = ET.Element('path')
        elem.text = f'{self.x + self.xP} {self.y + self.yP} m {self.x + self.xP} {self.y + self.yP - self.h} l {self.x + self.xP + self.w} {self.y + self.yP - self.h} l {self.x + self.xP + self.w} {self.y + self.yP} l h'

        self.addProperties(elem)

        return elem

