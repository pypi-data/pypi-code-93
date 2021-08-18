from ipey.primitive import Primitive
import xml.etree.ElementTree as ET
from collections import defaultdict
import copy

class Page:
    ID = 0

    def __init__(self):
        self.Layers = []
        self.Scene = list()
        self.Views = defaultdict(list)
        self.id = Page.ID
        Page.ID += 1
        return

    def clear(self):
        self.Layers = []
        self.Scene = list(Primitive)
        self.Views = defaultdict(list)

    def copyA(self):
        new = Page()

        for p in self.Scene:
            new.add(copy.deepcopy(p))

        new.Layers = copy.deepcopy(self.Layers)
        new.Views = copy.deepcopy(self.Views)

        return new

    '''
    ##################################################
    Scene
    ##################################################
    '''
    def add(self, p : Primitive) -> None:
        self.Scene.append(p)

    def addBefore(self, p1 : Primitive, p2 : Primitive) -> None:
        ind = self.Scene.index(p2)
        self.Scene.insert(ind, p1)

    def addAfter(self, p1 : Primitive, p2 : Primitive) -> None:
        ind = self.Scene.index(p2) + 1
        self.Scene.insert(ind, p1)

    def remove(self, p) -> None:
        self.Scene.remove(p)   
    
    # def moveToIndex(self, p: Primitive, index) -> None:
    #     indexOld = self.Scene.index(p)
    #     self.Scene.insert(index, self.Scene.pop(indexOld))

    # def moveBefore(self, p1 : Primitive, p2 : Primitive) -> None:


    '''
    ##################################################
    Layers
    ##################################################
    '''
    def createLayer(self, name):
        self.Layers.append(name)

        return name

    def removeLayer(self, name):

        return

    '''
    ##################################################
    Views
    ##################################################
    '''
    def createView(self, name, layers = None):
        if layers:
            self.Views[name].extend(layers)
        else:
            self.Views.setdefault(name)

    def addToView(self, name, layers):
        if name in self.Views:
            self.Views[name].extend(layers)

    '''
    ##################################################
    Drawing
    ##################################################
    '''
    def draw(self) -> ET.Element:
        page = ET.Element('page')

        for element in self.Scene:
            el = element.draw()
            page.append(el)

        return page

    '''
    ##################################################
    Overwritten
    ##################################################
    '''

    def __str__(self) -> str:
        return self.Scene.__str__()