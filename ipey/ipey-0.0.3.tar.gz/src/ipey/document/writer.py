import xml.etree.ElementTree as ET
import datetime 
import configparser
import pkg_resources
from xml.dom import minidom
import os

class IpeOptions:
    def __init__(self, settings_path = None):
        config = configparser.ConfigParser()

        if settings_path:
            config.read(settings_path)
        else:
            settings = pkg_resources.resource_filename(__name__, '../static/settings.ini')
            config.read(settings)                                     
        
        self.__dict__['_IPE_VERSION'] = config['IPE']['VERSION']
        self.__dict__['_IPE_CREATOR'] = config['IPE']['CREATOR']
        
        self.__dict__['_DRAWING_UNBOUND'] = config.getboolean('DRAWING', 'UNBOUND')
        self.__dict__['_DRAWING_WIDTH'] = config.getfloat('DRAWING', 'WIDTH')
        self.__dict__['_DRAWING_HEIGHT'] = config.getfloat('DRAWING', 'HEIGHT')
        self.__dict__['_DRAWING_MARGIN'] = config.getfloat('DRAWING','MARGIN')


class Writer:

    def __init__(self, settings_path = None, styles = []):
        self._options = IpeOptions(settings_path)
        self.styles = []

    def write(self, pages, path, size):
        ipe = ET.Element('ipe')
        ipe.set('version', self._options._IPE_VERSION)
        ipe.set('creator', self._options._IPE_CREATOR)

        info = ET.SubElement(ipe, 'info')

        timeNow = datetime.datetime.now().strftime("%Y%M%d%H%M%S")
        info.set('created', f'D:{timeNow}')
        info.set('modified' , f'D:{timeNow}')

        self.appendStyle(ipe, self.styles)
        self.appendSize(ipe, size)

        for page in pages:
            ipe.append(page)

        xmlPath= os.path.join('' , path) 
        xmlstr= minidom.parseString(ET.tostring(ipe)).toprettyxml(indent = "   ")
        with open(xmlPath, "w") as f:
            f.write(xmlstr)
            f.close()

    def appendSize(self, ipe, size):
        pagesize = ET.SubElement(ipe, 'ipestyle') 
        layout = ET.SubElement(pagesize, 'layout')
        layout.set('paper', f'{size[0][1]} {size[1][1]}')
        layout.set('origin', f'0 0')
        layout.set('frame', f'{size[0][1]} {size[1][1]}') 

    def appendStyle(self, ipe, styles):
        '''
        Append a list of given stylesheets to the ipe drawing.
        '''
        basicPath = pkg_resources.resource_filename(__name__, '../static/basic.xml')
        basic = ET.parse(basicPath).getroot()
        ipe.append(basic)

        for style in styles:
            s = ET.parse(style).getroot()
            ipe.append(s)