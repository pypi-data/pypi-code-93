import xmltodict
from html import unescape
from os import system, remove
from os.path import exists
from collections import OrderedDict
from ..config import Config
from ..mysql import RetrieveBaseInfo
from ..tools import createDir, prettyXML, getXML, sleep, findAllNumsWithRe, average


class Node:
    def __init__(self, resourceID='', text='', contentDesc='', bounds=''):
        self.resourceID = resourceID
        self.text = text
        self.contentDesc = contentDesc
        self.bounds = bounds


class UIAutomator:
    def __init__(self, deviceSN):
        self.device = RetrieveBaseInfo(deviceSN)
        self.cmd = 'adb -s %s ' % self.device.IP
        self.node = Node()
        self.xml = ''
        self.dicts = []

    def getScreen(self):
        system(self.cmd + 'exec-out screencap -p > CurrentUIHierarchy/%s.png' % self.device.SN)

    def tap(self, cP, interval=1):
        x, y = cP
        print('正在让%s点击(%d,%d)' % (self.device.SN, x, y))
        system(self.cmd + 'shell input tap %d %d' % (x, y))
        sleep(interval, Config.debug, Config.debug)

    def click(self, resourceID='', text='', contentDesc='', xml='', bounds='', offset_x=0, offset_y=0):
        cP = self.getCP(resourceID, text, contentDesc, xml, bounds)
        if cP and text:
            print('检测到【%s】' % text)
        if not cP:
            return False
        x, y = cP
        cP = x+offset_x, y+offset_y
        self.tap(cP)
        return True

    def getCP(self, resourceID='', text='', contentDesc='', xml='', bounds=''):
        bounds = self.getBounds(resourceID, text, contentDesc, xml, bounds)
        if not bounds:
            return False
        x1, y1, x2, y2 = findAllNumsWithRe(bounds)
        x = average(x1, x2)
        y = average(y1, y2)
        return x, y

    def getBounds(self, resourceID, text='', contentDesc='', xml='', bounds=''):
        dic = self.getDict(resourceID, text, contentDesc, xml, bounds)
        if dic:
            return dic['@bounds']
        return False

    def getDict(self, resourceID='', text='', contentDesc='', xml='', bounds=''):
        self.node = Node(resourceID, text, contentDesc, bounds)
        if xml:
            self.xml = xml
        else:
            self.xml = self.getCurrentUIHierarchy()
        dic = self.depthFirstSearch(xmltodict.parse(self.xml))
        if dic:
            dic.update({'@text': unescape(dic['@text'])})
        return dic

    def getDicts(self, resourceID='', text='', contentDesc='', xml='', bounds=''):
        self.dicts = []
        self.node = Node(resourceID, text, contentDesc, bounds)
        if xml:
            self.xml = xml
        else:
            self.xml = self.getCurrentUIHierarchy()
        self.depthFirstSearchDicts(xmltodict.parse(self.xml))
        return self.dicts

    def isTargetNode(self, dic):
        if type(dic) in (str, list):
            return False
        if '@resource-id' not in dic.keys():
            return False
        if self.node.resourceID:
            if dic['@resource-id'] == self.node.resourceID:
                if self.node.text:
                    if self.node.text in unescape(dic['@text']):
                        return True
                    return False
                elif self.node.contentDesc:
                    if unescape(dic['@content-desc']) == self.node.contentDesc:
                        return True
                    return False
                return True
        elif self.node.text:
            if self.node.text in unescape(dic['@text']):
                return True
            return False
        elif self.node.bounds:
            if self.isTargetBounds(self.node.bounds, dic['@bounds']):
                return True
            return False
        elif self.node.contentDesc:
            if self.node.contentDesc in unescape(dic['@content-desc']):
                return True
            return False
        return False

    @classmethod
    def isTargetBounds(cls, targetBounds, srcBounds):
        x1, y1, x2, y2 = findAllNumsWithRe(targetBounds)
        x3, y3, x4, y4 = findAllNumsWithRe(srcBounds)
        return x1 in (-1, x3) and y1 in (-1, y3) and x2 in (-1, x4) and y2 in (-1, y4)

    def depthFirstSearch(self, dic):
        if type(dic) == OrderedDict:
            if self.isTargetNode(dic):
                return dic
            for i in dic.keys():
                if self.isTargetNode(dic[i]):
                    return dic[i]
                res = self.depthFirstSearch(dic[i])
                if res:
                    return res
        elif type(dic) == list:
            for i in dic:
                res = self.depthFirstSearch(i)
                if res:
                    return res

    def depthFirstSearchDicts(self, dic):
        if type(dic) == OrderedDict:
            if self.isTargetNode(dic):
                self.dicts.append(dic)
            for i in dic.keys():
                if self.isTargetNode(dic[i]):
                    self.dicts.append(dic[i])
                res = self.depthFirstSearchDicts(dic[i])
                if res:
                    return res
        elif type(dic) == list:
            for i in dic:
                res = self.depthFirstSearchDicts(i)
                if res:
                    self.dicts.append(res)

    def getCurrentUIHierarchy(self, pretty=False):
        system(self.cmd + 'shell rm /sdcard/window_dump.xml')
        cmd = self.cmd + 'shell uiautomator dump /sdcard/window_dump.xml'
        if Config.debug:
            print(cmd)
        system(cmd)
        dirName = 'CurrentUIHierarchy'
        createDir(dirName)
        filePath = '%s/%s.xml' % (dirName, self.device.SN)
        print(filePath)
        if exists(filePath):
            remove(filePath)
        system('%spull /sdcard/window_dump.xml %s' % (self.cmd, filePath))
        if pretty:
            return prettyXML(filePath)
        return getXML(filePath)
