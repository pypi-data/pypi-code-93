import xml.etree.ElementTree as ET


def lst_dict_to_root(json):
    root = ET.Element("root")

    for elem in json:
        item = ET.SubElement(root, 'item')
        for (key, value) in elem.items():
            ET.SubElement(item, key).text = str(value)
    
    return root


