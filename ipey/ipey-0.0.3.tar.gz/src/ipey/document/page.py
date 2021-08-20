from ipey.primitive import Primitive
import xml.etree.ElementTree as ET
from collections import defaultdict
import copy

class Page:

    def __init__(self):
        self.Layers = []
        self.Scene = list()
        self.Views = defaultdict(set)
        return

    def clear(self):
        self.Layers = []
        self.Scene = list(Primitive)
        self.Views = defaultdict(set)

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
        '''
        Add an object to the scene. The object is appended which means it is the top-most element in the drawing.

        Parameters:
        p (Primitive): object which is added to the page

        Returns:
        None
        '''
        self.Scene.append(p)

    def addBefore(self, p1 : Primitive, p2 : Primitive) -> None:
        '''
        Add an object to the scene. The object is added to the drawing before the second object. This means it is drawn behind the second object.

        Parameters:
        p1 (Primitive): object which is added to the page
        p2 (Primitive): second object which gives the index 

        Returns:
        None
        '''
        ind = self.Scene.index(p2)
        self.Scene.insert(ind, p1)

    def addAfter(self, p1 : Primitive, p2 : Primitive) -> None:
        '''
        Add an object to the scene. The object is added to the drawing after the second object. This means it is drawn in front of the second object.

        Parameters:
        p1 (Primitive): object which is added to the page
        p2 (Primitive): second object which gives the index 

        Returns:
        None
        '''
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
        '''
        Create a new layer with a name as identifier. 

        Parameters:
        name (str): name of the layer

        Returns:
        layer (str)
        '''
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
            if isinstance(layers, str): layers = [ layers ]

            for layer in layers:
                self.Views[name].add(layer)
        else:
            self.Views.setdefault(name)

    def addToView(self, name, layers):
        if isinstance(layers, str): to_select = [ layers ]

        if name in self.Views:
            for layer in layers:
                self.Views[name].add(layer)

    def removeFromView(self, name, layers):
        if name in self.Views:
            for layer in layers:
                self.Views[name].remove(layer)

    '''
    ##################################################
    Drawing
    ##################################################
    '''
    def draw(self) -> ET.Element:
        page = ET.Element('page')

        checkLayers = set()

        for element in self.Scene:
            layer = element.layer

            if not layer:
                element.layer = 'alpha'
                layer = 'alpha'

            if not layer in checkLayers: 
                checkLayers.add(layer)
                l = ET.SubElement(page, 'layer')
                l.set('name', layer)

        for view, layers in self.Views.items():

            nonEmptyLayers = []

            for l in layers:
                if l in checkLayers:
                    nonEmptyLayers.append(l)

            if len(nonEmptyLayers) < 1:
                continue

            s = ''
            for layer in nonEmptyLayers:
                s += f'{layer} '

            v = ET.SubElement(page, 'view')
            v.set('layers', s)
            v.set('active', layer[0])

        for element in self.Scene:
            el = element.draw()
            page.append(el)

        return page

    def getLayers(self) -> list:
        layers = set()
        for element in self.Scene:
            layer = element.layer

            if layer:
                layers.add(layer)
        
        return layers

    '''
    ##################################################
    Overwritten
    ##################################################
    '''

    def __str__(self) -> str:
        return self.Scene.__str__()