from enum import Enum
import os
from typing import List
from xml.dom import minidom
from ipey.document.document import Document
import xml.etree.ElementTree as ET

from ipey.document.page import Page
from ipey.primitive.group import Group
from ipey.primitive.line import Line
from ipey.primitive.polygon import Polygon
from ipey.primitive.primitive import Primitive
from ipey.primitive.spline import Spline, SplineType
from ipey.primitive.splinegon import Splinegon


xml_header = '''<?xml version="1.0"?>
<!DOCTYPE ipestyle SYSTEM "ipe.dtd">
'''

class PathType(Enum):

    C_PATH = 0
    O_PATH = 1
    BEZIER = 2
    CARDINAL = 3
    SPIRO = 4
    SPLINEGON = 5
    ELLIPSE = 6
    ARC = 7


class Reader:
            

    def __init__(self) -> None:
        pass

    def read(self, path) -> Document:
        self.path = path
        tree = ET.parse(path)
        root = tree.getroot()
        version = root.attrib['version']
        creator = root.attrib['creator']

        styles = []

        for child in root:
            if child.tag == "ipestyle":
                styles.append(self.handle_style(child))
        
        doc = Document(styles=styles)

        for child in root:
            if child.tag == "info":
                self.handle_info(child)
            elif child.tag == "preamble":
                self.handle_preamble(child)
            elif child.tag == "page":
                page = doc.createPage()
                self.handle_page(child, page)
            elif child.tag == "bitmap":
                self.handle_bitmap(child)
        
        return doc

    def handle_style(self, child):
        style_dir = os.path.join(os.path.dirname(self.path), os.path.splitext(os.path.basename(self.path))[0]+"_styles")
        if not os.path.exists(style_dir):
            os.makedirs(style_dir)
        style_name = child.attrib['name']
        style_path = os.path.join(style_dir, style_name+".isy")
        if os.path.exists(style_path):
            print(f"Overriding {style_path}")
        xmlstr = ET.tostring(child, encoding='unicode', method='xml')
        with open(style_path, 'w') as f:
            f.write(xml_header)
            f.write(xmlstr)
            f.close()
        return style_path

    def handle_page(self, page_elem, page: Page):
        active_layer = ""
        for child in page_elem:

            # adding a new Layer. Must happen first
            if child.tag == "layer":
                page.createLayer(child.attrib['name'])
            
            # adding a new View. Must happen second
            elif child.tag == "view":
                page.createView(child.attrib['active'], child.attrib['layers'].split())

            else:
                child_object, active_layer = self.handle_primitive_child(child, page, active_layer)
                child_object.layer = active_layer
                page.add(child_object)

    def handle_primitive_child(self, child, active_layer, layer_fixed=False):
        
        primitive_child = None
        # Update active layer IF necessary and we are not bound by a group
        if "layer" in child.attrib and not layer_fixed:
            active_layer = child.attrib["layer"]

        # from here any object could appear
        if child.tag == "group":
            # groups contain multiple objects again, so we call this method recursively
            primitive_child = Group()
            for object in child:
                # method is returning object and active layer. We only need the object
                primitive_child.add(self.handle_primitive_child(object, True)[0])
        elif child.tag == "text":
            raise NotImplementedError
        elif child.tag == "image":
            raise NotImplementedError
        elif child.tag == "use":
            raise NotImplementedError
        elif child.tag == "path":
            primitive_child = self.handle_path(child)
        
        return primitive_child, active_layer

    def handle_path(self, child) -> Primitive:
        # decide which kind of object we are handling
        object_type = self.decide_object(child)

        # add correct object to the page in the active layer
        if object_type == PathType.O_PATH:
            points = self.get_polyline_points(child.text)
            return Line(points)

        elif object_type == PathType.C_PATH:
            points = self.get_polyline_points(child.text)
            return Polygon(points)

        elif object_type == PathType.BEZIER:
            points = self.get_spline_points(child.text, spline_type=SplineType.BSPLINE)
            return Spline(points, splineType=SplineType.BSPLINE)

        elif object_type == PathType.CARDINAL:
            points = self.get_spline_points(child.text, spline_type=SplineType.CARDINAL)
            return Spline(points, splineType=SplineType.CARDINAL)

        elif object_type == PathType.SPIRO:
            points = self.get_spline_points(child.text, spline_type=SplineType.SPIRO)
            return Spline(points, splineType=SplineType.SPIRO)

        elif object_type == PathType.SPLINEGON:
            points = self.get_splinegon_points(child.text)
            return Splinegon(points)

        elif object_type == PathType.ELLIPSE:
            raise NotImplementedError

        elif object_type == PathType.ARC:
            raise NotImplementedError

    def decide_object(self, object):
        path = object.text
        if 'c' in path:
            object_type = PathType.BEZIER
        elif 'C' in path:
            object_type = PathType.CARDINAL
        elif 'L' in path:
            object_type = PathType.SPIRO
        elif 'e' in path:
            object_type = PathType.ELLIPSE
        elif 'a' in path:
            object_type = PathType.ARC
        elif 'u' in path:
            object_type = PathType.SPLINEGON
        elif 'h' in path:
            object_type = PathType.C_PATH
        else:
            object_type = PathType.O_PATH
            
        # print(f"The {object.attrib['stroke']} object is a {object_type}, which is {'NOT ' if 'u' not in path and 'h' not in path and 'e' not in path else ''}closed")
        return object_type

    def get_polyline_points(self, text) -> List:
        points = []
        tokens = text.replace("\n", " ").split()
        for i in range(0, 3*(len(tokens)//3), 3):
            points.append((float(tokens[i]), float(tokens[i+1])))
        return points

    def get_spline_points(self, text, spline_type) -> List:
        points = []
        tokens = text.replace("\n", " ").split()

        # adding starting point
        points.append((float(tokens[0]), float(tokens[1])))

        i = 3
        # skipping approximated points if spiro
        if spline_type == SplineType.SPIRO:
            while tokens[i] != '*':
                i += 1
            i += 1

        offset = 1
        # larger offset if cardinal
        if spline_type == SplineType.CARDINAL:
            offset = 2

        # adding remaining points
        for i in range(i, len(tokens)-offset, 2):
            points.append((float(tokens[i]), float(tokens[i+1])))

        return points

    def get_splinegon_points(self, text) -> List:
        points = []
        tokens = text.replace("\n", " ").split()
        for i in range(0, len(tokens)-1, 2):
            points.append((float(tokens[i]), float(tokens[i+1])))

        return points

    def handle_bitmap(self, child):
        raise NotImplementedError

    def handle_info(self, child):
        pass
        # raise NotImplementedError

    def handle_preamble(self, child):
        raise NotImplementedError


