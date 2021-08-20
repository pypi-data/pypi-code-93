from typing import Tuple
from ipey.document import Writer
from ipey.primitive import Primitive
from ipey.document import Page
import xml.etree.ElementTree as ET
import sys

class Margin:
    '''
    Wrapper class for document margin property.
    '''
    def __init__(self, top=64, bottom=64, left=64, right=64):
        '''
        Initialize a margin wrapper object with values for the four margins
        '''
        self.top = top
        self.bottom = bottom
        self.left = left
        self.right = right

class Document:
    '''
    Representation for an IPE drawing. 
    '''

    def __init__(self, settings_path=None, styles=[]) -> None:
        self.Writer = Writer(settings_path, styles)
        self.Pages = []
        self.crop = False
        self.width = 896
        self.height = 896
        self.margin = Margin()

    def clear(self):
        self.Pages = []

    def createPage(self) -> Page:
        page = Page()
        self.Pages.append(page)

        return page

    def copyPage(self, page : Page) -> Page:
        newPage = page.copyA()
        self.Pages.append(newPage)

        return newPage

    def getSize(self) -> Tuple[int, int]:
        minX = sys.maxsize
        maxX = -sys.maxsize - 1
        minY = sys.maxsize
        maxY = -sys.maxsize - 1

        if self.crop:
            for page in self.Pages:
                for elem in page.Scene:
                    (p1, p2) = elem.getBB()
                    minX = min(minX, p1[0], p2[0])
                    maxX = max(maxX, p1[0], p2[0])
                    minY = min(minY, p1[1], p2[1])
                    maxY = max(maxY, p1[1], p2[1])

            Primitive.xP = self.margin.left - minX
            Primitive.yP = self.margin.bottom - minY
            # for page in self.Pages:
            #     for elem in page.Scene:
            #         elem.pX = self.margin.left - minX
            #         elem.pY = self.margin.bottom - minY          

            return ((0, (maxX - minX) + self.margin.right + self.margin.left), (0, (maxY - minY) + self.margin.top + self.margin.bottom))
        else:
            return ((0, self.width), (0, self.height))

    def write(self, path):

        pages = []
        size = self.getSize()

        for page in self.Pages:
            p = page.draw()
            pages.append(p)

        
        self.Writer.write(pages, path, size)
    