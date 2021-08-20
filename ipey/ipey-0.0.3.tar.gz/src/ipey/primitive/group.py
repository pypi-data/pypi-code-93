from ipey.primitive import Primitive
import xml.etree.ElementTree as ET


class Group(Primitive):
    Elements = []

    def __init__(self, prototype=None):
        super().__init__(prototype=prototype)
        self.clear()

    def clear(self):
        self.Elements = []

    def add(self, p : Primitive):
        self.Elements.append(p)

    def remove(self, p : Primitive):
        self.Elements.remove(p)

    def draw(self):
        elem = ET.Element('group')
        self.addProperties(elem)

        for e in self.Elements:
            ee = e.draw()
            elem.append(ee)

        return elem