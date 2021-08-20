import xml.etree.ElementTree as et

def is_xml(xml_text) :
  try :
    x = et.fromstring(xml_text)
    return True
  except Exception as e:
    return False  


def pretty_xml(xml_file) :
  xml_doc = et.parse(xml_file)
  return (et.tostring(xml_doc, pretty_print=True).decode("utf-8")) 
  
  
def parse_xml(xml_text) :
  try :
    xml_obj = et.fromstring(xml_text)
    return xml_obj
  except Exception as e:
    return None  


def get_xml_elements(xml_obj,xpath,value=None):
  elements_found = []
  xml_elements = xml_obj.findall(xpath)
  for e in xml_elements:
    if value is not None and value == e.text:
      elements_found.append(e)
    if value is None: 
      elements_found.append(e)
  return elements_found    

  
def get_xml_value(xml_obj,xpath):
  xml_element = None
  xml_element = xml_obj.find(xpath)
  if xml_element is not None : 
    return xml_element.text
  else :
    return ""

def get_xml_values(xml_obj,xpath):
  xml_values = []
  xml_elements = xml_obj.findall(xpath)
  for e in xml_elements:
    xml_values.append(e.text)
  return xml_values

  
def get_xml_attributes(xml_obj, xpath, attrib):
  xml_attributes = []
  xml_elements = xml_obj.findall(xpath)
  for e in xml_elements:
    xml_attributes.append(e.get(attrib))
  return xml_attributes

def contain_xml_value(xml_obj, xpath, value):
  values = get_xml_values(xml_obj, xpath)
  if value in values: return True
  return False

def contain_xml_attribute(xml_obj, xpath, attrib, value):
  attrib_values = get_xml_attributes(xml_obj, xpath, attrib)
  if value in attrib_values: return True
  return False

  
if __name__ == "__main__":
  import fs_tools
  xml = parse_xml(fs_tools.read_file('C:/TEMP/test.xml'))
  print (xml)
  #print (get_xml_value(xml, "./LearningProductOrganisationOffering/LearningProductOrganisationOffering-LearningProductOrganisationOfferingRelationshipList/LearningProductOrganisationOffering-LearningProductOrganisationOfferingRelationship/LearningProductOrganisationOfferingTo/LearningProduct/ProductType/Code"))
  
  print ( get_xml_values(xml, "./country[rank='4']/gdppc"))

  
  pass    