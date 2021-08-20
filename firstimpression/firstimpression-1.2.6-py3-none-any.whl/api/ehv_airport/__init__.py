import os
import glob
from firstimpression import file
import lxml.html
import xml.etree.ElementTree as ET

from firstimpression.constants import APIS, TEMP_FOLDER, LOCAL_INTEGRATED_FOLDER
from firstimpression.file import update_directories_api, check_too_old, write_root_to_xml_files
from firstimpression.scala import variables, Log
from firstimpression.api.request import request


##################################################################################################
# LOGGING
##################################################################################################

script = 'Eindhoven Airport'

info = Log('INFO', script)
debug = Log('DEBUG', script)
warn = Log('WARN', script)
error = Log('ERROR', script)

##################################################################################################
# CONSTANTS
##################################################################################################

NAME = APIS['eindhoven']
URL = 'https://www.eindhovenairport.nl/nl/vertrektijden'

XML_FILENAME = 'flights.xml'
XML_FILENAME_CONTENT = 'flights*.xml'
XML_TEMP_PATH = os.path.join(TEMP_FOLDER, NAME, XML_FILENAME)
XML_LOCAL_PATH = os.path.join(LOCAL_INTEGRATED_FOLDER, NAME, XML_FILENAME_CONTENT)
MAX_FILE_AGE = 60 * 10

TABLE_FLIGHTS_XPATH = '//div[@id="skyguide"]/div/table'

##################################################################################################
# MAIN FUNCTIONS API
##################################################################################################

def run_api():

    debug.log('folder name: {}'.format(NAME))
    debug.log('temp path: {} - local path: {}'.format(XML_TEMP_PATH, XML_LOCAL_PATH))

    update_directories_api(NAME)

    if check_too_old(XML_TEMP_PATH, MAX_FILE_AGE):
        root = ET.Element("root")

        response = lxml.html.fromstring(request(URL).text)

        table = response.xpath(TABLE_FLIGHTS_XPATH)[0]

        for row in table.xpath('tr'):
            item = ET.Element("item")
            store = False
            column_number = 1

            for column in row.xpath('td'):
                column_text = column.xpath('text()')

                if len(column_text) == 0:
                    column_text.append('')
                
                if column_number == 1:
                    ET.SubElement(item, "departure_time").text = column_text[0]
                elif column_number == 2:
                    ET.SubElement(item, "flight_number").text = column_text[0]
                elif column_number == 3:
                    ET.SubElement(item, "route").text = column_text[0]
                elif column_number == 4:
                    ET.SubElement(item, "status").text = column_text[0]
                    if not "Vertrokken" in column_text[0]:
                        debug.log('flight {} already left'.format(item.findtext('flight_number')))
                        store = True
                elif column_number == 5:
                    pass
                
                column_number += 1
            
            if store:
                root.append(item)
        
        write_root_to_xml_files(root, XML_TEMP_PATH, NAME)
    else:
        debug.log('File not old enough to update')

def check_api():
    svars = variables()

    file_path = glob.glob(XML_LOCAL_PATH)

    if len(file_path) > 0:
        file_path = file_path[0]
        debug.log('glob filepath: {}'.format(file_path))

        if check_too_old(file_path, MAX_FILE_AGE):
            svars['skipscript'] = True
            info.log('file too old')
        else:
            svars['skipscript'] = False
    else:
        warn.log('File does not exists')
        svars['skipscript'] = True
        
    



##################################################################################################
# MEDIA FUNCTIONS
##################################################################################################


##################################################################################################
# GET FUNCTIONS
##################################################################################################


##################################################################################################
# PARSE FUNCTIONS
##################################################################################################
