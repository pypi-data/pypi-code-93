from lxml import etree
import cv2
import xml.dom.minidom
import numpy as np
import random
from time import sleep


class Item:
    node = None
    xpath = ""
    __text = ""
    __tempId = ""
    __x = 0.0
    __y = 0.0
    __z = 0
    __index_z = 0
    __height = 0.0
    __width = 0.0
    __className = ""
    __objectName = ""
    __opacity = 0.0
    __focus = None
    __enabled = None
    __visible = None
    device = None
    app = None
    surfaceHeight = 0
    surfaceWidth = 0
    surfaceX = 0
    surfaceY = 0
    rect = []

    def __init__(self, d=None, a=None, node=None, xpath=""):
        self.app = a
        self.device = d
        self.node = node
        self.xpath = xpath
        self.__refresh_attribute()

    def __refresh_node(self):
        self.device.refresh_layout()
        selector = etree.XML(self.device.xmlStr.encode('utf-8'))
        nodes = selector.xpath(self.xpath)
        if len(nodes) > 0 and selector.get("sopId") == self.app.sopId:
            self.node = nodes[0]

    def __refresh_attribute(self):
        self.__x = float(self.node.get("globalX"))
        self.__y = float(self.node.get("globalY"))
        self.__z = int(self.node.get("z"))
        self.__height = float(self.node.get("height"))
        self.__width = float(self.node.get("width"))
        self.__tempId = self.node.get("tempID")
        self.__text__ = self.node.get("text")
        self.__objectName = self.node.get("objectName")
        self.__className = self.node.tag
        self.__opacity = float(self.node.get("opacity"))
        self.__enabled = bool(int(self.node.get("enabled")))
        self.__visible = bool(int(self.node.get("visible")))
        self.__focus = bool(int(self.node.get("focus")))

    def x(self, refresh=False):
        if refresh:
            self.__refresh_node()
            self.__refresh_attribute()
        return self.__x

    def y(self, refresh=False):
        if refresh:
            self.__refresh_node()
            self.__refresh_attribute()
        return self.__y

    def z(self, refresh=False):
        if refresh:
            self.__refresh_node()
            self.__refresh_attribute()
        return self.__z

    def height(self, refresh=False):
        if refresh:
            self.__refresh_node()
            self.__refresh_attribute()
        return self.__height

    def width(self, refresh=False):
        if refresh:
            self.__refresh_node()
            self.__refresh_attribute()
        return self.__width

    def temp_id(self, refresh=False):
        if refresh:
            self.__refresh_node()
            self.__refresh_attribute()
        return self.__tempId

    def text(self, refresh=False):
        if refresh:
            self.__refresh_node()
            self.__refresh_attribute()
        return self.__text__

    def object_name(self, refresh=False):
        if refresh:
            self.__refresh_node()
            self.__refresh_attribute()
        return self.__objectName

    def class_name(self, refresh=False):
        if refresh:
            self.__refresh_node()
            self.__refresh_attribute()
        return self.__className

    def opacity(self, refresh=False):
        if refresh:
            self.__refresh_node()
            self.__refresh_attribute()
        return self.__opacity

    def enabled(self, refresh=False):
        if refresh:
            self.__refresh_node()
            self.__refresh_attribute()
        return self.__enabled

    def visible(self, refresh=False):
        if refresh:
            self.__refresh_node()
            self.__refresh_attribute()
        return self.__visible

    def focus(self, refresh=False):
        if refresh:
            self.__refresh_node()
            self.__refresh_attribute()
        return self.__focus

    def exist(self, timeout=None):
        if timeout is None:
            timeout = self.device.default_timeout
        for m_iter in range(0, timeout):
            if m_iter > 0:
                sleep(1)
            self.rect = self.__exist()
            if len(self.rect) > 0:
                return True
        return False

    def __exist(self):
        self.device.refresh_layout()
        tree = xml.dom.minidom.parseString(self.device.xmlStr)
        if tree.documentElement.childNodes.length > 0 and tree.documentElement.getAttribute("sopId") == self.app.sopId:
            surface = tree.documentElement.childNodes[0]
            self.surfaceHeight = round(float(surface.getAttribute("height")))
            self.surfaceWidth = round(float(surface.getAttribute("width")))
            self.surfaceX = round(float(surface.getAttribute("globalX")))
            self.surfaceY = round(float(surface.getAttribute("globalY")))
            image = self.__xml_tree_traversed(surface.childNodes, self.surfaceX, self.surfaceY, self.surfaceHeight,
                                              self.surfaceWidth)
            # cv2.imshow("s", image)
            # cv2.waitKey(0)
            b, g, r = cv2.split(image)
            if len(np.argwhere(r == 255)) > 0:
                return np.argwhere(r == 255)
            return []

    def __xml_tree_traversed(self, nodes, px, py, ph, pw):
        images = {}
        for node in nodes:
            x = round(float(node.getAttribute("globalX")))
            y = round(float(node.getAttribute("globalY")))
            height = round(float(node.getAttribute("height")))
            width = round(float(node.getAttribute("width")))
            if float(node.getAttribute("opacity")) != 0 \
                    and int(node.getAttribute("visible")) == 1 \
                    and node.nodeName != "CScrollDecorator" \
                    and node.nodeName != "QQuickShaderEffectSource" \
                    and node.nodeName != "PerformanceOverlay" \
                    and not (node.nodeName == "QQuickMouseArea" and node.childNodes.length == 0) \
                    and not (node.getAttribute("objectName") == "multitouchGrid" and int(node.getAttribute("enabled")) == 0) \
                    and x < (px + pw) \
                    and (x + width) > px \
                    and y < (py + ph) \
                    and (y + height) > py:
                if (width + x) > (pw + px) and x < px:
                    width = pw
                    x = px
                elif x < px:
                    width = width - (px - x)
                    x = px
                elif (width + x) > (pw + px):
                    width = width - ((width + x) - (pw + px))
                if (height + y) > (ph + py) and y < py:
                    height = ph
                    y = py
                elif y < py:
                    height = height - (py - y)
                    y = py
                elif (height + y) > (ph + py):
                    height = height - ((height + y) - (ph + py))
                index_z = int(node.getAttribute("z"))
                image = np.zeros((self.surfaceHeight + self.surfaceY, self.surfaceWidth + self.surfaceX),
                                 dtype=np.uint8)
                image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
                if node.nodeName != "QQuickLoader":
                    if node.getAttribute("tempID") == self.__tempId:
                        cv2.rectangle(image, (x, y), (x + width, y + height), (0, 0, 255), -1)
                    else:
                        cv2.rectangle(image, (x, y), (x + width, y + height), (255, 0, 0), -1)
                        # cv2.rectangle(image, (x, y), (x + width, y + height), (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)), -1)
                if node.childNodes.length > 0:
                    if int(node.getAttribute("clip")) == 1:
                        c_images = self.__xml_tree_traversed(node.childNodes, x, y, height, width)
                    else:
                        c_images = self.__xml_tree_traversed(node.childNodes, px, py, ph, pw)
                    image = self.__img_cover(image, c_images)
                if index_z in images.keys():
                    images[index_z] = self.__img_cover(images[index_z], image)
                else:
                    images[index_z] = image
        im_list = list(images.keys())
        im_list.sort()
        r_image = np.zeros((self.surfaceHeight + self.surfaceY, self.surfaceWidth + self.surfaceX), dtype=np.uint8)
        r_image = cv2.cvtColor(r_image, cv2.COLOR_GRAY2BGR)
        for index in im_list:
            r_image = self.__img_cover(r_image, images[index])
        return r_image

    @staticmethod
    def __img_cover(src1, src2):
        rows, cols, channels = src2.shape
        roi = src1[0:rows, 0:cols]
        src2_2gray = cv2.cvtColor(src2, cv2.COLOR_BGR2GRAY)
        ret, mask = cv2.threshold(src2_2gray, 1, 255, cv2.THRESH_BINARY)
        image_bg = cv2.bitwise_and(roi, roi, mask=mask)
        image = cv2.subtract(src1, image_bg)
        image = cv2.add(image, src2)
        return image

    def click(self):
        x = self.__x + (self.__width / 2)
        y = self.__y + (self.__height / 2)
        self.device.click(x, y)

    def click_exist(self, timeout=None):
        if timeout is None:
            timeout = self.device.default_timeout
        for m_iter in range(0, timeout):
            if m_iter > 0:
                sleep(1)
            if self.exist():
                self.device.click(self.rect[2][1], self.rect[2][0])
                return True
        return False

    def submit_string(self, text):
        self.click()
        self.device.submit_string(text)
